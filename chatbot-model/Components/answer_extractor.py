import config
import operator
from transformers import QuestionAnsweringPipeline


class AnswerExtractor:

    # load pretrained model and tokenizer and create pipeline to generate answers
    def __init__(self, tokenizer, model):
        tokenizer = tokenizer.from_pretrained(config.MODEL_PATH)
        model = model.from_pretrained(config.MODEL_PATH)
        
        self.nlp = QuestionAnsweringPipeline(model=model, tokenizer=tokenizer)

    # given question and related passages, it returns answers dictionary sorted 
    # in descending order of scores
    def extract(self, question, passages):
        
        answers = []
        
        for passage in passages:
            try:
                currAnswer = self.nlp(question=question, context=passage)
                currAnswer['text'] = passage
                answers.append(currAnswer)
            except KeyError:
                pass
        answers.sort(key=operator.itemgetter('score'), reverse=True)
        return answers