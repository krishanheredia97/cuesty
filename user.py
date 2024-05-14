from datetime import datetime
import data_manager  # Import the data_manager module


class User:
    def __init__(self, user_id, username):
        self.data = {
            "user_id": user_id,
            "username": username,
            "habits": []
        }
        self.load_user_data()  # Load existing user data

    def load_user_data(self):
        # Load user data to check for existing habits
        data = data_manager.load_data()
        user_id = self.data["user_id"]
        if user_id in data:
            self.data["habits"] = data[user_id].get("habits", [])

    def add_habit(self, habit_name, data_manager):
        # Capitalize habit name and ensure it is within the 30 character limit
        habit_name = habit_name.capitalize()[:30]

        # Check for duplicate habits
        for habit in self.data["habits"]:
            if habit["name"] == habit_name:
                return False, f"'{habit_name}' already exists."

        habit = {
            "name": habit_name,
            "creation_time": datetime.utcnow().isoformat(),
            "status": "Active",
            "last_activation_time": datetime.utcnow().isoformat(),
            "last_relapse_time": None
        }
        data_manager.update_user_habits(self.data, habit)
        return True, f"'{habit_name}' has been added to your habits!"

    def relapse_habit(self, habit_name, data_manager):
        habit_name = habit_name.capitalize()[:30]
        for habit in self.data["habits"]:
            if habit["name"] == habit_name:
                habit["status"] = "Inactive"
                habit["last_relapse_time"] = datetime.utcnow().isoformat()
        data_manager.save_data(self.data)

    def activate_habit(self, habit_name, data_manager):
        habit_name = habit_name.capitalize()[:30]
        for habit in self.data["habits"]:
            if habit["name"] == habit_name:
                habit["status"] = "Active"
                habit["last_activation_time"] = datetime.utcnow().isoformat()
        data_manager.save_data(self.data)
