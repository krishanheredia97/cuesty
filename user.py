class User:
    def __init__(self, user_id, username):
        self.data = {
            "user_id": user_id,
            "username": username,
            "habits": []
        }

    def add_habit(self, habit_name, data_manager):
        data_manager.update_user_habits(self.data, habit_name)
