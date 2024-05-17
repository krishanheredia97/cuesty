# user.py

import data_manager
import datetime

class User:
    def __init__(self, user_id, username):
        self.data = {
            "user_id": user_id,
            "username": username,
            "vices": [],
            "user_rewards": [],  # Add user_rewards to user data
            "global_relapse_count": 0,
            "global_quit_count": 0,
            "level": 1,
            "xp": 0,  # Cumulative XP
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

    def add_vice(self, vice_name):
        vice_name = vice_name.capitalize()
        if any(vice["name"] == vice_name for vice in self.data["vices"]):
            return False, f"'{vice_name}' already exists."
        new_vice = {
            "name": vice_name,
            "status": "Active",
            "log": [{"action": "created", "timestamp": self.current_time()}],
            "relapse_count": 0,
            "quit_count": 1,
            "last_update": self.current_time()
        }
        self.data["vices"].append(new_vice)
        self.data["global_quit_count"] += 1
        self.save_user_data()
        return True, f"'{vice_name}' has been added to your vices!"

    def relapse_vice(self, vice_name):
        self.calculate_rewards()
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
        self.calculate_rewards()
        for vice in self.data["vices"]:
            if vice["name"] == vice_name and vice["status"] == "Inactive":
                vice["status"] = "Active"
                vice["log"].append({"action": "quit", "timestamp": self.current_time()})
                vice["quit_count"] += 1
                vice["last_update"] = self.current_time()
                self.data["global_quit_count"] += 1
                self.save_user_data()
                return True, f"You have quit '{vice_name}'."
        return False, f"'{vice_name}' is not an inactive vice."

    def get_active_vices(self):
        return [vice["name"] for vice in self.data["vices"] if vice["status"] == "Active"]

    def get_inactive_vices(self):
        return [vice["name"] for vice in self.data["vices"] if vice["status"] == "Inactive"]

    def add_reward(self, reward_name):
        reward_name = reward_name.capitalize()
        if any(reward["name"] == reward_name for reward in self.data["user_rewards"]):
            return False, f"'{reward_name}' already exists."
        new_reward = {
            "name": reward_name,
            "redeemed": "no",
            "cost": "Pending",
            "log": [{"action": "created", "timestamp": self.current_time()}]
        }
        self.data["user_rewards"].append(new_reward)
        self.save_user_data()
        return True, f"'{reward_name}' has been added to your rewards!"

    def calculate_rewards(self):
        current_time = datetime.datetime.utcnow()
        for vice in self.data["vices"]:
            if vice["status"] == "Active":
                last_update_time = datetime.datetime.fromisoformat(vice["last_update"])
                elapsed_seconds = (current_time - last_update_time).total_seconds()
                self.data["xp"] += int(elapsed_seconds // 60)  # Add 1 XP per minute
                self.data["gp"] += int(elapsed_seconds // 7200)  # Add 1 GP every 2 hours
                self.data["honor"] += int(elapsed_seconds // 86400)  # Add 1 Honor every 24 hours
                self.level_up()  # Check for level up
                vice["last_update"] = current_time.isoformat()

    def level_up(self):
        while True:
            xp_required = 3000 * (1.4 ** (self.data["level"] - 1))
            if self.data["xp"] >= xp_required:
                self.data["level"] += 1
            else:
                break

    def current_time(self):
        return datetime.datetime.utcnow().isoformat()
