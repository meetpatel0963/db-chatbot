# DB_Chat-Bot_Project

# Chatbot Model Setup

## To download SQUAD v2.0 Dataset 
```
mkdir squad
wget https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json -O squad/train-v2.0.json
wget https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json -O squad/dev-v2.0.json
```

## To install torch-xla
```
pip install cloud-tpu-client==0.10 https://storage.googleapis.com/tpu-pytorch/wheels/torch_xla-1.9-cp37-cp37m-linux_x86_64.whl
```

## To setup TPU device
```
import torch_xla
import torch_xla.core.xla_model as xm
device = xm.xla_device()
```

## To install required libs
```
pip install wheel click==7.1.1
pip install spacy transformers datasets neuralcoref sentencepiece html2text bert-extractive-summarizer gensim==3.6.0 bs4 torch torchvision fastapi nest-asyncio pyngrok uvicorn
python3 -m spacy download en
python3 -m spacy download en_core_web_md
```

## To test the model when context and questions are given by user
```
python <path_to_project_dir>/predict.py
```

## To fine-tune Model on SQUAD dataset
### Specify configuration variables related to Model (for ex. bert-large-uncased-whole-word-masking) and path to dataset (json files).
### Make sure to set the TRAIN flag to True in config.py
```
python <path_to_project_dir>/main.py
```

## To run the Model-API (FastAPI)
```
python <path_to_project_dir>/model-api.py
```

# React Setup

### Install Node and npm on your machine.
### Commands for Linux
```
apt install nodejs
apt install npm
npm install
```

