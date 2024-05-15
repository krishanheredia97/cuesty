from vice import Vice
import data_manager

class ViceManager:
    def __init__(self, user_data):
        self.user_data = user_data
        self.user_data["vices"] = [Vice.from_dict(h) if isinstance(h, dict) else h for h in self.user_data["vices"]]

    def add_vice(self, vice_name):
        vice_name = vice_name.capitalize()
        if any(vice.name == vice_name for vice in self.user_data["vices"]):
            return False, f"'{vice_name}' already exists."
        new_vice = Vice(vice_name)
        self.user_data["vices"].append(new_vice)
        self.user_data["global_quit_count"] += 1
        self.save_user_data()
        return True, f"'{vice_name}' has been added to your vices!"

    def relapse_vice(self, vice_name):
        for vice in self.user_data["vices"]:
            if vice.name == vice_name and vice.status == "Active":
                vice.relapse()
                self.user_data["global_relapse_count"] += 1
                self.save_user_data()
                return True, f"You have relapsed on '{vice_name}'."
        return False, f"'{vice_name}' is not an active vice."

    def quit_vice(self, vice_name):
        for vice in self.user_data["vices"]:
            if vice.name == vice_name and vice.status == "Inactive":
                vice.quit()
                self.user_data["global_quit_count"] += 1
                self.save_user_data()
                return True, f"You have quit '{vice_name}'."
        return False, f"'{vice_name}' is not an inactive vice."

    def get_active_vices(self):
        return [vice.name for vice in self.user_data["vices"] if vice.status == "Active"]

    def get_inactive_vices(self):
        return [vice.name for vice in self.user_data["vices"] if vice.status == "Inactive"]

    def save_user_data(self):
        self.user_data["vices"] = [vice.to_dict() for vice in self.user_data["vices"]]
        data_manager.save_data(self.user_data)
