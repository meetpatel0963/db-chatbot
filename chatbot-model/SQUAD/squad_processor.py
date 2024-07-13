import json
from pathlib import Path


def read_squad(path):
    path = Path(path)
    with open(path, 'rb') as f:
        squad = json.load(f)

    contexts = []
    questions = []
    answers = []
    for obj in squad['data']:
        for passage in obj['paragraphs']:
            context = passage['context']
            for pair in passage['qas']:
                question = pair['question']
                for answer in pair['answers']:
                    contexts.append(context)
                    questions.append(question)
                    answers.append(answer)

    return contexts, questions, answers


def add_end_idx(answers, contexts):
    for answer, context in zip(answers, contexts):
        answer_txt = answer['text']
        start_idx = answer['answer_start']
        end_idx = start_idx + len(answer_txt)

        if context[start_idx:end_idx] == answer_txt:
            answer['answer_end'] = end_idx
        elif context[start_idx-1:end_idx-1] == answer_txt:
            answer['answer_start'] = start_idx - 1
            answer['answer_end'] = end_idx - 1     
        elif context[start_idx-2:end_idx-2] == answer_txt:
            answer['answer_start'] = start_idx - 2
            answer['answer_end'] = end_idx - 2     
            
            
def add_token_positions(encodings, answers, tokenizer):
    start_positions = []
    end_positions = []
    for i in range(len(answers)):
        start_positions.append(encodings.char_to_token(i, answers[i]['answer_start']))
        end_positions.append(encodings.char_to_token(i, answers[i]['answer_end'] - 1))
        
        if start_positions[-1] is None:
            start_positions[-1] = tokenizer.model_max_length
        if end_positions[-1] is None:
            end_positions[-1] = tokenizer.model_max_length
    encodings.update({'start_positions': start_positions, 'end_positions': end_positions})

    
    