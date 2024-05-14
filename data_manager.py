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
    with open(FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

def update_user_habits(user_data, habit_name):
    data = load_data()
    user_id = user_data["user_id"]
    if user_id not in data:
        user_data["habits"] = [habit_name]  # Initialize with the new habit
        data[user_id] = user_data
    else:
        data[user_id]["habits"].append(habit_name)  # Append new habit to existing list
    save_data(data)
