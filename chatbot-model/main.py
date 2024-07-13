import os
import spacy
import time
# import torch_xla
# import torch_xla.core.xla_model as xm
from transformers import TrainingArguments, Trainer

import config
from SQUAD.squad_dataset import SquadDataset
from SQUAD.squad_processor import read_squad, add_end_idx, add_token_positions
from model import Model
from utils import get_tokenizer, get_model, get_doc_retriever

from Components.passage_retrieval import PassageRetrieval
from Components.query_processor import QueryProcessor
from Components.answer_extractor import AnswerExtractor


def main():

    if config.DO_TRAIN:
        print('> Reading SQUAD v2.0...')

        # Read Training and Validation data and extract contexts, questions and answers
        train_contexts, train_questions, train_answers = read_squad(config.TRAIN_PATH)
        val_contexts, val_questions, val_answers = read_squad(config.VAL_PATH)

        print('> SQUAD v2.0 Loaded.')

        # Add end index - Answers contain only start index by default
        add_end_idx(train_answers, train_contexts)
        add_end_idx(val_answers, val_contexts)


        print('> Loading Model...')

        # Load the model and apply tokenization
        model = Model()
        train_encodings = model.tokenize(train_contexts, train_questions)
        val_encodings = model.tokenize(val_contexts, val_questions)

        print('> Model Loaded.')


        # Add token possitions to encodings
        add_token_positions(train_encodings, train_answers, model.tokenizer)
        add_token_positions(val_encodings, val_answers, model.tokenizer)

        # Create datasets
        train_dataset = SquadDataset(train_encodings)
        val_dataset = SquadDataset(val_encodings)


        # Setting up the TPU device
        # device = xm.xla_device()

        # An instance of Training arguments
        training_args = TrainingArguments(
            output_dir=config.OUT_DIR,
            num_train_epochs=config.NUM_EPOCHS,
            per_device_train_batch_size=config.PER_DEVICE_TRAIN_BATCH_SIZE,
            per_device_eval_batch_size=config.PER_DEVICE_VAL_BATCH_SIZE,
            warmup_steps=config.WARMUP_STEPS,
            weight_decay=config.WEIGHT_DECAY,
            logging_dir=config.LOG_DIR,
            logging_steps=config.LOGGING_STEPS,
            label_names = ["start_positions", "end_positions"]
        )

        # An instance of Trainer
        trainer = Trainer(
            model=model.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset
        )


        print('> Training...')

        # To train the Model
        trainer.train()



    if config.DO_EVAL:
        SPACY_MODEL = 'en_core_web_sm'
        nlp = spacy.load(SPACY_MODEL, disable=['ner', 'parser', 'textcat'])
        query_processor = QueryProcessor(nlp)
        
        document_retriever = get_doc_retriever(config.USERNAME, config.TOKEN, nlp)
        
        passage_retriever = PassageRetrieval(nlp)

        tokenizer = get_tokenizer()
        model = get_model()
        answer_extractor = AnswerExtractor(tokenizer, model)

        print('\nEnter "stop" in question to STOP.\n')
        while True:
            main_start_time = time.time()
            question = input('\nEnter question > ')

            if question.lower() == 'stop':
                break

            start_time = time.time()
            query = query_processor.generate_query(question)
            print('---- query processor: {} sec ----'.format(time.time() - start_time))

            start_time = time.time()
            docs = None
            if isinstance(document_retriever, list):
                docs = []
                for retriever in document_retriever:
                    docs.extend(retriever.search(question))
            else:
                docs = document_retriever.search(question)

            if len(docs) == 0:
                print("Invalid username or password!")
                break
            print('---- doc retriever: {} sec ----'.format(time.time() - start_time))

            start_time = time.time()
            passage_retriever.fit(docs)
            passages = passage_retriever.most_similar(question)
            print('---- passage retriever: {} sec ----'.format(time.time() - start_time))

            start_time = time.time()
            answers = answer_extractor.extract(question, passages)
            print('---- answer extractor: {} sec ----'.format(time.time() - start_time))

            if answers[0]['text'].startswith(config.CONFLUENCE['CODE_PREFIX']):
                answers[0]['answer'] = ' '.join(answers[0]['text'].split(' ')[1:])

            print('---- main: {} sec ----'.format(time.time() - main_start_time))
            
            if config.PRINT_ALL_ANSWERS:
                for i in range(len(answers)):
                    print("{} > {}".format(i, answers[i]))
            else:
                print(answers[0]['answer'])

if __name__ == "__main__":
    main()

