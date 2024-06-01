import json

def load_quest_data():
    with open('quest_data.json', 'r') as file:
        return json.load(file)

def save_quest_data(data):
    with open('quest_data.json', 'w') as file:
        json.dump(data, file, indent=4)
