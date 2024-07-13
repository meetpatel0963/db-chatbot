apt-get update
apt install python3-venv
python3 -m venv chatbot-model
source chatbot-model/bin/activate

pip install wheel click==7.1.1

pip install spacy transformers datasets neuralcoref sentencepiece html2text bert-extractive-summarizer gensim==3.6.0 bs4 torch torchvision
python3 -m spacy download en
python3 -m spacy download en_core_web_md
