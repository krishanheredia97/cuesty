from datetime import datetime
import data_manager

class User:
    def __init__(self, user_id, username):
        self.data = {
            "user_id": user_id,
            "username": username,
            "habits": []
        }
        self.load_user_data()

    def load_user_data(self):
        data = data_manager.load_data()
        user_id = self.data["user_id"]
        if user_id in data:
            self.data["habits"] = data[user_id].get("habits", [])

    def add_habit(self, habit_name, data_manager):
        habit_name = habit_name.capitalize()[:30]
        for habit in self.data["habits"]:
            if habit["name"] == habit_name:
                return False, f"'{habit_name}' already exists."

        habit = {
            "name": habit_name,
            "creation_time": datetime.utcnow().isoformat(),
            "status": "Active",
            "last_activation_time": datetime.utcnow().isoformat(),
            "last_relapse_time": None,
            "log": [
                {
                    "action": "created",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
        self.data["habits"].append(habit)
        data_manager.save_data({self.data["user_id"]: self.data})
        return True, f"'{habit_name}' has been added to your habits!"

    def get_active_habits(self):
        return [habit["name"] for habit in self.data["habits"] if habit["status"] == "Active"]

    def relapse_habit(self, habit_name):
        habit_name = habit_name.capitalize()[:30]
        for habit in self.data["habits"]:
            if habit["name"] == habit_name and habit["status"] == "Active":
                habit["status"] = "Inactive"
                habit["last_relapse_time"] = datetime.utcnow().isoformat()
                habit["log"].append({
                    "action": "relapsed",
                    "timestamp": datetime.utcnow().isoformat()
                })
                data_manager.save_data({self.data["user_id"]: self.data})
                return True, f"You have relapsed on '{habit_name}'."
        return False, f"No active habit found with the name '{habit_name}'."

    def activate_habit(self, habit_name, data_manager):
        habit_name = habit_name.capitalize()[:30]
        for habit in self.data["habits"]:
            if habit["name"] == habit_name and habit["status"] == "Inactive":
                habit["status"] = "Active"
                habit["last_activation_time"] = datetime.utcnow().isoformat()
                habit["log"].append({
                    "action": "reactivated",
                    "timestamp": datetime.utcnow().isoformat()
                })
                data_manager.save_data({self.data["user_id"]: self.data})
                return True, f"You have reactivated '{habit_name}'."
        return False, f"No inactive habit found with the name '{habit_name}'."
