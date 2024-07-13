import config
from utils import get_tokenizer, get_model


class Model():
    """
        To load the pretrained Model and Tokenizer from Huggingface and apply Tokenization on contexts and questions.
    """
    
    def __init__(self):
        self.tokenizer = get_tokenizer().from_pretrained(config.MODEL_TYPE)
        self.model = get_model().from_pretrained(config.MODEL_TYPE)
    
    def tokenize(self, contexts, questions):
        return self.tokenizer(contexts, questions, truncation=True, padding=True)