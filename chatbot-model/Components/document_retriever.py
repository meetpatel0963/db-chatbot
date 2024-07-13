import os
import csv
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
import html2text
from summarizer import TransformerSummarizer
from gensim.summarization.bm25 import BM25


class ConfluenceDocumentRetriever:
    """
      This class is for retrieving Documents from atlassian confluence api and returing the pages
      in the form of List after appropriate preprocessing.

      search: Search the pages from an API and return passages and tables in the form of list of strings.
          - First, It will get all the pages for a user.
          - If summary of some page is not present in summary file, then it will generate and store the summary for that page.
          - Apply BM25 between user's question (query) and summary of docs and get TOP N docs to search using API.
          - Search the most relavant N pages (extracted in previous) step though API.
          - Extract text and tables from these pages and convert it into a list of passages.
      generate_summary: Given a page ID, generate summary of that page content using GPT-2 Model.
      get_relavant_pages: Extract the most relavant N pages using BM25 between query and summary of the docs.
      search_pages: Get metadata of all the pages of a user and return a list of page ids.
      search_page: Given a page id, get html of that page using an API.
      extract_text: To extract text data from given html data of a page.
      extract_passages: To extract passages from a text data of a page.
      extract tables: To extract tables from given html data of a page in below format:
                      col1: val1, col2: val2, ... , colN: valN
                      Rows within a table are separated by "  |  ".
      update_confluence_summary_db: To update the confluence summary csv - delete the summary of deleted docs
                                    and add the summary for newly created docs.
    """

    def __init__(self, userName, token, nlp, confluence, domain, projectkey):
        self.domain = domain
        self.page_ids = []
        self.userName = userName
        self.token = token
        self.SPACEKEY = projectkey
        self.CODE_PREFIX = confluence['CODE_PREFIX']
        self.CONFLUENCE_SUMMARY_DB = confluence['CONFLUENCE_SUMMARY_DB']
        self.min_summary_words = confluence['MIN_SUMMARY_WORDS']
        self.update_confluence_summary = confluence['UPDATE_CONFLUENCE_SUMMARY']
        self.SEPARATOR = confluence['SEPARATOR']
        self.tokenize = lambda text: [token.lemma_ for token in nlp(text)]
        self.GPT2_model = TransformerSummarizer(transformer_type="GPT2", transformer_model_key="gpt2-medium")
        self.invalid = False

        self.validate()

        if self.invalid is False:
            if not os.path.exists(confluence['CONFLUENCE_SUMMARY_DB']):
                with open(confluence['CONFLUENCE_SUMMARY_DB'], 'w') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(['page_id', 'summary', 'passages'])

            if self.update_confluence_summary:
                self.update_confluence_summary = False
                self.search_pages()
                self.update_confluence_summary_db()

    def validate(self):
        url = 'https://' + self.domain + '.atlassian.net/wiki/rest/api/search?cql='
        if self.SPACEKEY:
            url = url + 'space=' + self.SPACEKEY + ' and '
        url = url + 'type=page'
        requestResponse = requests.get(url, auth=(self.userName, self.token))
        if requestResponse.ok is False:
            self.invalid = True
    
    def search_page(self, page_id, expand=False):
        if expand:
            suffix = '?expand=' + expand
        else:
            suffix = ''

        url = 'https://' + self.domain + '.atlassian.net/wiki/rest/api/content/' + page_id + suffix
        response = requests.get(url, auth=(self.userName, self.token))
        response.encoding = 'utf8'

        return json.loads(response.text)

    def search_pages(self):
        url = 'https://' + self.domain + '.atlassian.net/wiki/rest/api/search?cql='
        if self.SPACEKEY:
            url = url + 'space=' + self.SPACEKEY + ' and '
        url = url + 'type=page'
        response = requests.get(url, auth=(self.userName, self.token))
        obj = response.json()

        page_ids = []
        for page in obj['results']:
            page_ids.append(page['content']['id'])

        self.page_ids = page_ids

    def extract_text(self, html_data):
        soup = BeautifulSoup(html_data, features='html.parser')

        # kill all script and style elements
        for script in soup(['script', 'style', 'table']):
            script.extract()

        h = html2text.HTML2Text()
        return h.handle(str(soup))

    def extract_passages(self, text):

        # replacing all heading tags with $
        for i in range(6):
            text = text.replace((6 - i) * '#', '$')

        # making passages by splitting text by $
        passages = text.split('$')

        # improving text representation
        passages = [passage.replace('*', '') for passage in passages]
        passages = [passage.replace('\n', ' ') for passage in passages]
        passages = [" ".join(passage.split()) for passage in passages]
        passages = [passage for passage in passages if (len(passage))]

        return passages

    def extract_codes(self, html_data):
        soup = BeautifulSoup(html_data, 'html.parser')
        codes = []

        for tag in soup.findAll('ac:structured-macro', {'ac:name': "code"}):
            code = ' ' + tag.previous_sibling.get_text() + ' : ' + tag.get_text().replace('\n', ', ')
            codes.append(self.CODE_PREFIX + code)

        return codes

    def extract_tables(self, html_data):
        txt_data = []

        try:
            tables = pd.read_html(html_data)
            for df in tables:
                cols = list(df.columns)
                df = df.fillna('None')
                r = ''
                for idx, row in df.iterrows():
                    for i in range(len(cols)):
                        r += str(cols[i]) + ': ' + str(row[cols[i]])
                        r += ', ' if i < len(cols) - 1 else '  |  '
                txt_data.append(r)
        except:
            pass

        return txt_data

    def get_relavant_pages(self, df, question, topn=2):
        summary_docs = []
        for idx, row in df.iterrows():
            if str(row['page_id']) in self.page_ids:
                summary_docs.append(row['summary'])

        corpus = [self.tokenize(doc) for doc in summary_docs]
        self.bm25 = BM25(corpus)

        tokens = self.tokenize(question)
        average_idf = sum(float(val) for val in self.bm25.idf.values()) / len(self.bm25.idf)
        scores = self.bm25.get_scores(tokens, average_idf)
        pairs = [(s, i) for i, s in enumerate(scores)]
        pairs.sort(reverse=True)
        topn_docs = [summary_docs[i] for _, i in pairs[:topn]]
        mask = df['summary'].isin(topn_docs)

        return list(map(str, df.loc[mask]['page_id']))

    def generate_summary(self, page_id):
        page_json = self.search_page(page_id, 'body.storage')
        page_html = page_json['body']['storage']['value']
        tables = self.extract_tables(page_html)
        codes = self.extract_codes(page_html)
        text = self.extract_text(page_html)
        passages = self.extract_passages(text)

        csv_tables = self.SEPARATOR.join(tables)
        csv_codes = self.SEPARATOR.join(codes)
        csv_passages = self.SEPARATOR.join(passages)
        csv_final = csv_passages + self.SEPARATOR + csv_tables + self.SEPARATOR + csv_codes

        data = ' '.join(passages)
        tables = ' '.join(tables)
        codes = ' '.join(codes)
        data_length = len(data.split(' '))
        summary = ''
        if data_length <= self.min_summary_words:
            summary = data + '  |  ' + codes + '  |  ' + tables
        else:
            summary = self.GPT2_model(data,
                                      ratio=self.min_summary_words / data_length) + '  |  ' + codes + '  |  ' + tables

        return summary, csv_final

    def update_confluence_summary_db(self):
        df = pd.read_csv(self.CONFLUENCE_SUMMARY_DB)
        csv_page_ids = df['page_id'].tolist()

        new_data = []
        for page_id in self.page_ids:
            if int(page_id) not in csv_page_ids:
                summary, passage = self.generate_summary(page_id)
                if not summary:
                    continue
                new_data.append([int(page_id), summary, passage])

        for idx, row in df.iterrows():
            if str(row['page_id']) in self.page_ids:
                new_data.append([row['page_id'], row['summary'], row['passages']])

        if new_data:
            with open(self.CONFLUENCE_SUMMARY_DB, 'w+') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['page_id', 'summary', 'passages'])
                csvwriter.writerows(new_data)

    def get_passages_from_string(self, text):
        passages = text.split(self.SEPARATOR)
        passages = [passage for passage in passages if len(passage)]
        return passages

    def search(self, question):
        docs = []
        if self.invalid:
            return docs

        df = pd.read_csv(self.CONFLUENCE_SUMMARY_DB)
        self.search_pages()
        topn_page_ids = self.get_relavant_pages(df, question)

        for idx, row in df.iterrows():
            if str(row['page_id']) in topn_page_ids:
                passages = self.get_passages_from_string(row['passages'])
                docs.extend(passages)

        return docs


# ------------------------------------------------------------------------------------------------------------------------


class JiraDocumentRetriever():
    """
         This class is for retrieving Documents from JIRA API and returing the data (objects - tasks, issues etc.)
         in the form of stories.

         search: Search for items (issues, tasks, stories etc.) for a given Project using Jira API.
         get_total_items: Get total Number of items for a given project.
         search_items: Get metadata about each item for a given project.
         extract_passages: Extract required fields from the object, parse it and return a list of strings.
    """

    def __init__(self, username, token, jira, domain, projectkey):
        self.userName = username
        self.token = token
        self.domain = domain
        self.projectKey = projectkey
        self.fields = jira['FIELDS']
        self.invalid = False
        self.validate()

    def validate(self):
        url = 'https://' + self.domain + '.atlassian.net//rest/api/2/search?jql=project=' + self.projectKey + '&maxResults=0'
        requestResponse = requests.get(url, auth=(self.userName, self.token))
        if requestResponse.ok is False:
            self.invalid = True

    def get_total_items(self):
        url = 'https://' + self.domain + '.atlassian.net//rest/api/2/search?jql=project=' + self.projectKey + '&maxResults=0'

        response = requests.get(url, auth=(self.userName, self.token))
        response.encoding = 'utf8'
        json_data = json.loads(response.text)

        return json_data['total']

    def search_items(self, total):
        suffix = '&fields=' + self.fields if self.fields else ''
        url = 'https://' + self.domain + '.atlassian.net//rest/api/2/search?jql=project=' + self.projectKey + suffix + '&maxResults=1000&startAt='

        for startIndex in range(0, total, 1000):
            new_url = url + str(startIndex)
            response = requests.get(new_url, auth=(self.userName, self.token))
            response.encoding = 'utf8'

        return json.loads(response.text)

    def extract_passages(self, obj):
        fieldMap = {
            'creator': 'created by',
            'reporter': 'reported by',
            'displayName': 'name',
            'hasVoted': 'has voted',
            'emailAddress': 'email'
        }
        keyMap = {
            'creator': ['accountId', 'emailAddress', 'displayName', 'timeZone'],
            'reporter': ['accountId', 'emailAddress', 'displayName', 'timeZone'],
            'priority': ['name'],
            'progress': ['progress', 'total'],
            'resolution': ['description'],
            'votes': ['votes', 'hasVoted'],
            'assignee': ['accountId', 'emailAddress', 'displayName', 'timeZone'],
            'status': ['name'],
        }

        passages = []
        txt = 'maxResults: ' + str(obj['maxResults']) + ', '
        txt += 'total: ' + str(obj['total'])
        passages.append(txt)

        for issue in obj['issues']:
            cur_issue = {}
            cur_issue['key'] = issue['key']

            for key, value in issue['fields'].items():
                if isinstance(value, dict):
                    cur_issue[key] = {}
                    for k in keyMap[key]:
                        cur_issue[key][k] = value[k]
                else:
                    cur_issue[key] = value

            new_issue_dict = {}
            for key, value in cur_issue.items():
                if isinstance(value, dict):
                    new_issue_dict[key] = {}
                    for subkey, subvalue in value.items():
                        if subkey in fieldMap.keys():
                            new_issue_dict[key][fieldMap[subkey]] = subvalue
                        else:
                            new_issue_dict[key][subkey] = subvalue
                else:
                    if key in fieldMap.keys():
                        new_issue_dict[fieldMap[key]] = value
                    else:
                        new_issue_dict[key] = value

            passages.append(json.dumps(new_issue_dict))

        return passages

    def create_story(self, obj):
        fields = obj['fields']
        assigned_to = fields['assignee']['displayName'] if fields['assignee'] is not None else 'No One'
        sprint_name = fields['customfield_10020'][0]['name'] if len(fields['customfield_10020']) != 0 else 'no'
        sprint_state = fields['customfield_10020'][0]['state'] if fields['customfield_10020'] != 0 else 'not defined'
        parent_issue = fields['parent']['fields']['summary'] if 'parent' in fields.keys() else 'None'
        subtasks = fields['subtasks']
        story = f'''
                The task of {fields['summary']} is started by {fields['creator']['displayName']} and this task assigned to {assigned_to} by {fields['creator']['displayName']} and it's key is {obj['key']}. This task was created by 
            {fields['creator']['displayName']} at {fields['created']}.{assigned_to} is working on this task .{fields['summary']} has a priority of {fields['priority']['name']}
            and the status of this task is {fields['status']['name']}. This task belongs to {sprint_name} sprint and the sprint is in {sprint_state} state. Number of votes for this task is {fields['votes']['votes']}.
            The task of {fields['summary']} is the subtask or child of {parent_issue}.
            {parent_issue} is the parent of {fields['summary']}.
        '''
        
        if fields['description']:
            story += f"Description: {fields['description']}"

        story += 'Time spent on this task is '
        if fields['timespent']:
            story += fields['timespent'] + '.'
        else:
            story += 'None.'
            
        if fields['resolutiondate']:
            resolution_meta = fields['resolutiondate'].split('T')
            resolutiondate = resolution_meta[0]
            resolutiontime = resolution_meta[1].split('.')[0]
            story += f"This task was resolved on {resolutiondate} at {resolutiontime}."
        else:
            story += "This task is not resolved yet."
        
        if len(subtasks) > 0:
            subtask_story = f"The subtasks or children of {fields['summary']}"
            if len(subtasks) == 1:
                subtask_story += " is "
            else:
                subtask_story += " are "
            for subtask in subtasks:
                subtask_story += f"{subtask['fields']['summary']}, "
            story += subtask_story
        else:
            subtask_story = f"The subtasks or children of {fields['summary']} are none."
            story += subtask_story
        return story

    def create_stories(self, objs):
        docs = []
        txt = 'maxResults: ' + str(objs['maxResults']) + ', '
        txt = 'There are total ' + str(objs['total']) + ' tasks in the project ' + self.projectKey + '.'
        docs.append(txt)

        for obj in objs['issues']:
            docs.append(self.create_story(obj))
        return docs

    def search(self, question):
        docs = []
        if self.invalid:
            return docs
        total_items = self.get_total_items()
        objs = self.search_items(total_items)
        docs = self.create_stories(objs)
        return docs
    
    
# ------------------------------------------------------------------------------------------------------------------------


class BitBucketRetriever():
    """
    This class is for retrieving Documents from BitBuckets API and returing the data (objects - commits, issues, branches, workspaces, repositories etc.) in the form of stories.

    search_issues: Search for all the issues from a given repository of a given workspace and create a story from each issue object. These stories will be returned as a list of strings.
    """
  
    def __init__(self, username, password, domain, projectkey):
        self.userName = username
        self.password = password
        self.workspace = domain
        self.repository = projectkey
        self.invalid = False
        self.validate()
    
    def validate(self):
        requestUrl = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{self.repository}/issues"
        requestResponse = requests.get(requestUrl, auth=(self.userName, self.password))
        if requestResponse.ok is False:
            self.invalid = True

    def search_all_repositories(self, workspace):
        requestUrl = f"https://api.bitbucket.org/2.0/repositories/{workspace}/"
        repo_response = requests.get(requestUrl, auth=(self.userName, self.password))
        repositories = repo_response.json()
        return repositories

    def search_all_workspaces(self):
        requestUrl = f"https://api.bitbucket.org/2.0/workspaces/"
        workspaces = requests.get(requestUrl, auth=(self.userName, self.password))
        workspaces = workspaces.json()
        return workspaces

    def search_all_branches(self, workspace, repository):
        requestUrl = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repository}/refs/branches/"
        branches = requests.get(requestUrl, auth=(self.userName, self.password))
        branches = branches.json()
        return branches

    def search_issues(self):
        requestUrl = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{self.repository}/issues"
        requestResponse = requests.get(requestUrl, auth=(self.userName, self.password))
        objs = requestResponse.json()

        assignee_dict = {}
        total_issues = objs['size']

        issue_docs = []
        for obj in objs['values']:
            assignee = obj['assignee']['display_name'] if obj['assignee'] else 'None'

            if (assignee in assignee_dict.keys()):
                assignee_dict[assignee] = assignee_dict[assignee] + 1
            else:
                assignee_dict[assignee] = 1

            created_meta = obj['created_on'].split('T')
            created_date = created_meta[0]
            created_time = created_meta[1].split('.')[0]

            updated_meta = obj['created_on'].split('T')
            updated_date = updated_meta[0]
            updated_time = updated_meta[1].split('.')[0]

            issue_type = obj['kind']
            issue_title = obj['title']
            reporter_name = obj['reporter']['display_name']
            votes = obj['votes']
            watches = obj['watches']
            status = obj['state']
            repo_name = obj['repository']['name']
            priority = obj['priority']

            issue_story = f"A {issue_type} {issue_title} was reported by {reporter_name}. This {issue_type} was reported on {created_date} at {created_time}. This {issue_type} is assigned to {assignee}. It has {votes} number of votes and {watches} number of watches. It was last updated on {updated_date} at {updated_time}. Currently, this {issue_type} is in {status} state. It belongs to {repo_name} repository. The priority of this {issue_type} is {priority}."

            if obj['content']:
                issue_story += ' Description: ' + obj['content']['raw']

            issue_docs.append(issue_story)

        issue_story = f"Total {total_issues} issues are there in {self.repository}. "

        for key, value in assignee_dict.items():
            issue_story += f"{value} issues have been assigned to {key} in repository named {self.repository}. "

        issue_docs.append(issue_story)

        return issue_docs


    def search_commits(self):
        requestUrl = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{self.repository}/commits"
        requestResponse = requests.get(requestUrl, auth=(self.userName, self.password))
        objs = requestResponse.json()

        commit_docs = []
        for obj in objs['values']:
            message = obj['message'].strip()

            created_meta = obj['date'].split('T')
            created_date = created_meta[0]
            created_time = created_meta[1].split('+')[0]

            repo_name = obj['repository']['name']

            author_meta = obj['author']['raw'].split('<')
            author_name = author_meta[0][:-1]
            author_mailID = author_meta[1][:-1]

            commit_hash = obj['hash']
            parent_hash = obj['parents'][0]['hash'] if len(obj['parents']) > 0 else 'does not exist'

            commit_story = f"The commit {message} was done by {author_name} on {created_date} at {created_time}. The author of this commit is {author_name}. {author_name}'s mail is {author_mailID}. The hash of this commit is {commit_hash}. The hash of the parent commit of the commit {message} is {parent_hash}. This commit belongs to {repo_name} repository."
            commit_docs.append(commit_story)

        return commit_docs


    def search(self, question):
        docs = []
        if self.invalid:
            return docs
        issue_docs = self.search_issues()
        commit_docs = self.search_commits()
        docs.extend(issue_docs)
        docs.extend(commit_docs)

        return docs