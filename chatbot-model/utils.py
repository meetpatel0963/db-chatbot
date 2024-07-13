import config
from transformers import BertTokenizerFast, BertForQuestionAnswering
from transformers import DistilBertTokenizerFast, DistilBertForQuestionAnswering
from transformers import AlbertTokenizerFast, AlbertForQuestionAnswering
from Components.document_retriever import ConfluenceDocumentRetriever, JiraDocumentRetriever, BitBucketRetriever



# Pretrained Tokenizers from Huggingface
tokenizer = {
    'bert-base-uncased': BertTokenizerFast,
    'distilbert-base-uncased': DistilBertTokenizerFast,
    'albert-base-v2': AlbertTokenizerFast,
    'bert-large-uncased-whole-word-masking': BertTokenizerFast,
}

# Pretrained Models from Huggingface
model = {
    'bert-base-uncased': BertForQuestionAnswering,
    'distilbert-base-uncased': DistilBertForQuestionAnswering,
    'albert-base-v2': AlbertForQuestionAnswering,
    'bert-large-uncased-whole-word-masking': BertForQuestionAnswering,
}

# Doc Retriever Classes
doc_retriever = {
    'confluence': lambda username, password, nlp, domain, projectkey: ConfluenceDocumentRetriever(username, password, nlp, config.CONFLUENCE, domain, projectkey),
    'jira': lambda username, password, nlp, domain, projectkey: JiraDocumentRetriever(username, password, config.JIRA, domain, projectkey),
    'bitbucket': lambda username, password, nlp, domain, projectkey: BitBucketRetriever(username, password, domain, projectkey),
}

def get_tokenizer():
    """
        Returns an object to load pretrained Tokenizer according to MODEL_TYPE config variable.
    """
    
    return tokenizer[config.MODEL_TYPE]


def get_model():
    """
        Returns an object to load pretrained Model according to MODEL_TYPE config variable.
    """
    
    return model[config.MODEL_TYPE]

def get_doc_retriever(confluence_username, confluence_password, bitbucket_username, bitbucket_password, nlp, doc_retriever_key, domain, projectkey):
    """
        Returns a DocumentRetriever based on doc_retriever_key (confluence OR jira OR BitBucket).
    """

    if doc_retriever_key != "all":
        if doc_retriever_key == "bitbucket":
            return doc_retriever[doc_retriever_key](bitbucket_username, bitbucket_password, nlp, domain, projectkey)     
        else:
            return doc_retriever[doc_retriever_key](confluence_username, confluence_password, nlp, domain, projectkey)       
    
    doc_retriever_key = ["confluence", "jira", "bitbucket"]
    
    ret = []
    for key in doc_retriever_key:
        if doc_retriever_key == "bitbucket":
            ret.append(doc_retriever[doc_retriever_key](bitbucket_username, bitbucket_password, nlp, domain, projectkey))
        else:
            ret.append(doc_retriever[doc_retriever_key](confluence_username, confluence_password, nlp, domain, projectkey))       
    
    return ret

