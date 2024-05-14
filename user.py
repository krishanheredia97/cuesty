from datetime import datetime
import data_manager

class User:
    def __init__(self, user_id, username):
        self.data = {
            "user_id": user_id,
            "username": username,
            "level": 1,
            "xp": 0,
            "gp": 0,
            "honor": 0,
            "vices": [],
            "global_relapse_count": 0,
            "global_quit_count": 0
        }
        self.load_user_data()

    def load_user_data(self):
        data = data_manager.load_data()
        user_id = self.data["user_id"]
        if user_id in data:
            self.data.update(data[user_id])

    def add_vice(self, vice_name, data_manager):
        vice_name = vice_name.capitalize()[:30]
        for vice in self.data["vices"]:
            if vice["name"] == vice_name:
                return False, f"'{vice_name}' already exists."

        vice = {
            "name": vice_name,
            "creation_time": datetime.utcnow().replace(microsecond=0).isoformat(),
            "status": "Active",
            "last_activation_time": datetime.utcnow().replace(microsecond=0).isoformat(),
            "last_relapse_time": None,
            "relapse_count": 0,
            "quit_count": 1,
            "log": [
                {
                    "action": "created",
                    "timestamp": datetime.utcnow().replace(microsecond=0).isoformat()
                }
            ]
        }
        self.data["vices"].append(vice)
        self.data["global_quit_count"] += 1
        data_manager.save_data({self.data["user_id"]: self.data})
        return True, f"'{vice_name}' has been added to your vices!"

    def get_active_vices(self):
        return [vice["name"] for vice in self.data["vices"] if vice["status"] == "Active"]

    def relapse_vice(self, vice_name):
        vice_name = vice_name.capitalize()[:30]
        for vice in self.data["vices"]:
            if vice["name"] == vice_name and vice["status"] == "Active":
                vice["status"] = "Inactive"
                vice["last_relapse_time"] = datetime.utcnow().replace(microsecond=0).isoformat()
                vice["relapse_count"] += 1
                vice["log"].append({
                    "action": "relapsed",
                    "timestamp": datetime.utcnow().replace(microsecond=0).isoformat()
                })
                self.data["global_relapse_count"] += 1
                data_manager.save_data({self.data["user_id"]: self.data})
                return True, f"You have relapsed on '{vice_name}'."
        return False, f"No active vice found with the name '{vice_name}'."

    def activate_vice(self, vice_name, data_manager):
        vice_name = vice_name.capitalize()[:30]
        for vice in self.data["vices"]:
            if vice["name"] == vice_name and vice["status"] == "Inactive":
                vice["status"] = "Active"
                vice["last_activation_time"] = datetime.utcnow().replace(microsecond=0).isoformat()
                vice["quit_count"] += 1
                vice["log"].append({
                    "action": "reactivated",
                    "timestamp": datetime.utcnow().replace(microsecond=0).isoformat()
                })
                self.data["global_quit_count"] += 1
                data_manager.save_data({self.data["user_id"]: self.data})
                return True, f"You have reactivated '{vice_name}'."
        return False, f"No inactive vice found with the name '{vice_name}'."
