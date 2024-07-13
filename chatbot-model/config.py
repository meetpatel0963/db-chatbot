"""
    Global Configuration Variables
"""


TRAIN_PATH = '/content/squad/train-v2.0.json'
VAL_PATH = '/content/squad/dev-v2.0.json'
MODEL_TYPE = 'bert-large-uncased-whole-word-masking'
OUT_DIR = '/content/results'
NUM_EPOCHS = 3
API_URL = "https://en.wikipedia.org/w/api.php"
PER_DEVICE_TRAIN_BATCH_SIZE = 16
PER_DEVICE_VAL_BATCH_SIZE = 64
WARMUP_STEPS = 500
WEIGHT_DECAY = 0.01
LOG_DIR = '/content/logs'
LOGGING_STEPS = 10
MODEL_PATH = './bert/'
DO_TRAIN = False
DO_EVAL = True
PRINT_ALL_ANSWERS = True
USERNAME = ''
TOKEN = ''
CONFLUENCE = {
    'CONFLUENCE_SUMMARY_DB': './confluence_summary_db.csv',
    'MIN_SUMMARY_WORDS': 200,
    'UPDATE_CONFLUENCE_SUMMARY': False,
    'CODE_PREFIX': '###code###',
    'SEPARATOR': '###SEP###',
}
JIRA = {
    'FIELDS': 'summary,assignee,creator,created,priority,votes,status,customfield_10020,parent,subtasks,description,resolutiondate,timespent',
}
