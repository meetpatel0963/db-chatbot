import os

import requests
import config
from dotenv import load_dotenv

load_dotenv()

# domain = config.DOMAIN
# userName = config.USERNAME
# token = config.TOKEN


def test_search_page(page_id, expand=False):
    if expand:
        suffix = '?expand=' + expand
    else:
        suffix = ''

    url = 'https://' + domain + '.atlassian.net/wiki/rest/api/content/' + page_id + suffix
    response = requests.get(url, auth=(userName, token))
    response.encoding = 'utf8'
    page_json = json.loads(response.text)
    html_data = json_data['body']['storage']['value']

    print('> Page HTML : ')
    print(html_data)


def test_search_pages():
    url = 'https://' + domain + '.atlassian.net/wiki/rest/api/search?cql=type=page'
    response = requests.get(url, auth=(userName, token))
    obj = requestResponse.json()

    page_ids = []
    for page in obj['results']:
        page_ids.append(page['cotent']['id'])

    print('> Page IDs : ')
    print(page_ids)


def test_jira_issues():
    url = "https://db-chatbot.atlassian.net/rest/api/3/search?fields=assignee,summary,creator,created,priority,votes"
    headers = {
        "Authorization": f"Basic {os.getenv('CONFLUENCE_API_KEY')}",
    }
    res = requests.get(url,headers=headers)
    # print(res.reason)
    res = res.json()
    #print("Res",res)
    res = res['issues'][0]
    fields = res['fields']
    assigned_to = res['fields']['assignee']['displayName'] if res['fields']['assignee'] is not None else 'No One'
    # print("Fields:",fields['assignee'])
    story = f'''
                    The task of {fields['summary']} is assigned to {assigned_to} and it's key is {res['key']}. This task was created at {fields['created']} by 
                {fields['creator']['displayName']}. {fields['summary']} has a priority of {fields['priority']['name']}
                and the status of the task is {fields['priority']['name']}. The total votes for this task is {fields['votes']['votes']}
            '''
    print(story)

test_jira_issues()