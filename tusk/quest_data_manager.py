import json
import os

QUEST_DATA_FILE = 'quest_data.json'

def ensure_quest_data_file():
    if not os.path.exists(QUEST_DATA_FILE):
        with open(QUEST_DATA_FILE, 'w') as file:
            json.dump({}, file)

def load_quest_data():
    with open(QUEST_DATA_FILE, 'r') as file:
        return json.load(file)

def save_quest_data(quest_data):
    with open(QUEST_DATA_FILE, 'w') as file:
        json.dump(quest_data, file, indent=4)

ensure_quest_data_file()
