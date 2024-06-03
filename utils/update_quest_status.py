import firebase_admin
from firebase_admin import credentials, db
import sys
import os

firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS')
cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cuesty-424dc-default-rtdb.firebaseio.com/'
})

def update_quest_status(quest_id, new_status):
    ref = db.reference(f'quests/{quest_id}/Quest_Main')
    ref.update({'quest_status': new_status})
    print(f"Quest {quest_id} status updated to {new_status}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python update_quest_status.py <quest_id> <status>")
        sys.exit(1)

    quest_id = sys.argv[1]
    status = sys.argv[2]
    update_quest_status(quest_id, status)
