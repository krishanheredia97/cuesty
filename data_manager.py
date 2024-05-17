# data_manager.py

import json
from pathlib import Path

FILE_PATH = Path('user_data.json')

def load_data():
    if not FILE_PATH.exists():
        return {}
    with open(FILE_PATH, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    existing_data = load_data()
    existing_data[data["user_id"]] = data
    with open(FILE_PATH, 'w') as file:
        json.dump(existing_data, file, indent=4)
