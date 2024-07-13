import config
from transformers import QuestionAnsweringPipeline
from utils import get_tokenizer, get_model


# Create an instance of Tokenizer and Model
tokenizer = get_tokenizer()
model = get_model()

# Loading the trained Tokenizer and Model
tokenizer = tokenizer.from_pretrained(config.MODEL_PATH) 
model = model.from_pretrained(config.MODEL_PATH)

# NLP Pipeline for Question-Answering
nlp = QuestionAnsweringPipeline(model=model, tokenizer=tokenizer)

# To test the Model on sample contexts and questions
context = input('Enter context > ')
print('\nEnter "stop" in question to STOP.\n')

while True:
    question = input('\nEnter question > ')
    if question.lower() == 'stop':
        break
    answer = nlp(question=question, context=context)
    print('answer > ', answer)
    
    