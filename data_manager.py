from firebase_admin import db

# Function to load user data from Firebase
def load_data(user_id):
    ref = db.reference(f'users/{user_id}')
    return ref.get() or {}

# Function to save user data to Firebase
def save_data(data):
    ref = db.reference(f'users/{data["user_id"]}')
    ref.set(data)
