import data_manager  # Ensure data_manager is imported
import datetime

class User:
    def __init__(self, user_id, username):
        self.data = {
            "user_id": user_id,
            "username": username,
            "vices": [],
            "global_relapse_count": 0,
            "global_quit_count": 0,
            "level": 1,
            "xp": 0,
            "gp": 0,
            "honor": 0,
        }
        self.load_user_data()

    def load_user_data(self):
        data = data_manager.load_data()
        if self.data["user_id"] in data:
            self.data.update(data[self.data["user_id"]])

    def save_user_data(self):
        data_manager.save_data(self.data)

    def add_vice(self, vice_name, data_manager):
        vice_name = vice_name.capitalize()
        if any(vice["name"] == vice_name for vice in self.data["vices"]):
            return False, f"'{vice_name}' already exists."
        new_vice = {
            "name": vice_name,
            "status": "Active",
            "log": [{"action": "created", "timestamp": self.current_time()}],
            "relapse_count": 0,
            "quit_count": 1,
        }
        self.data["vices"].append(new_vice)
        self.data["global_quit_count"] += 1
        self.save_user_data()
        return True, f"'{vice_name}' has been added to your vices!"

    def relapse_vice(self, vice_name):
        for vice in self.data["vices"]:
            if vice["name"] == vice_name and vice["status"] == "Active":
                vice["status"] = "Inactive"
                vice["log"].append({"action": "relapsed", "timestamp": self.current_time()})
                vice["relapse_count"] += 1
                self.data["global_relapse_count"] += 1
                self.save_user_data()
                return True, f"You have relapsed on '{vice_name}'."
        return False, f"'{vice_name}' is not an active vice."

    def quit_vice(self, vice_name):
        for vice in self.data["vices"]:
            if vice["name"] == vice_name and vice["status"] == "Inactive":
                vice["status"] = "Active"
                vice["log"].append({"action": "quit", "timestamp": self.current_time()})
                vice["quit_count"] += 1
                self.data["global_quit_count"] += 1
                self.save_user_data()
                return True, f"You have quit '{vice_name}'."
        return False, f"'{vice_name}' is not an inactive vice."

    def get_active_vices(self):
        return [vice["name"] for vice in self.data["vices"] if vice["status"] == "Active"]

    def get_inactive_vices(self):
        return [vice["name"] for vice in self.data["vices"] if vice["status"] == "Inactive"]

    def current_time(self):
        return datetime.datetime.utcnow().isoformat()
