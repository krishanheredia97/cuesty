from firebase_admin import db


# Function to load user data from Firebase
def load_data(user_id):
    ref = db.reference(f'users/{user_id}')
    return ref.get() or {}


# Function to save user data to Firebase
def save_data(data):
    ref = db.reference(f'users/{data["user_id"]}')
    ref.set(data)


# Function to load quest data from Firebase
def load_quest_data(quest_id):
    ref = db.reference(f'quests/{quest_id}')
    return ref.get() or {}


# Function to save quest data to Firebase
def save_quest_data(data):
    if 'Quest_Main' not in data or 'quest_id' not in data['Quest_Main']:
        raise KeyError("The quest data does not contain a 'Quest_Main' key or 'quest_id' key within 'Quest_Main'.")

    quest_id = data['Quest_Main']['quest_id']
    ref = db.reference(f'quests/{quest_id}')
    ref.set(data)
