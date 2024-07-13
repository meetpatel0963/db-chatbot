import os
import spacy
from transformers import TrainingArguments, Trainer

import config
from SQUAD.squad_dataset import SquadDataset
from SQUAD.squad_processor import read_squad, add_end_idx, add_token_positions
from model import Model
from utils import get_tokenizer, get_model, get_doc_retriever

from Components.passage_retrieval import PassageRetrieval
from Components.query_processor import QueryProcessor
from Components.answer_extractor import AnswerExtractor

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import nest_asyncio
from pyngrok import ngrok


SPACY_MODEL = 'en_core_web_sm'
nlp = spacy.load(SPACY_MODEL, disable=['ner', 'parser', 'textcat'])
query_processor = QueryProcessor(nlp)

passage_retriever = PassageRetrieval(nlp)

tokenizer = get_tokenizer()
model = get_model()
answer_extractor = AnswerExtractor(tokenizer, model)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/query/')
def get_answer(confluence_username: str, confluence_password: str, bitbucket_username: str, bitbucket_password: str, question: str, doc_retriever_key: str, domain: str, projectkey: str):
    query = query_processor.generate_query(question)
    document_retriever = get_doc_retriever(confluence_username, confluence_password, bitbucket_username, bitbucket_password, nlp, doc_retriever_key, domain, projectkey)
    docs = None

    if not isinstance(document_retriever, list):
        docs = document_retriever.search(question)
    else:
        docs = []
        for ret in document_retriever:
            docs.extend(ret.search(question))

    if len(docs) == 0:
        return { 'answers': None, 'error': 'Invalid username or password! Type /restart to reset username and password.' }
    
    passage_retriever.fit(docs)
    passages = passage_retriever.most_similar(question)
    answers = answer_extractor.extract(question, passages)
    
    if answers[0]['text'].startswith(config.CONFLUENCE['CODE_PREFIX']):
        answers[0]['answer'] = ' '.join(answers[0]['text'].split(' ')[1:])

    return {'answers': answers, 'error': None }


# ngrok_tunnel = ngrok.connect(8000)
# print('Public URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
uvicorn.run(app, port=8000, host='0.0.0.0')