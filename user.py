import data_manager
from habit_manager import HabitManager

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
        self.habit_manager = HabitManager(self.data)

    def load_user_data(self):
        data = data_manager.load_data()
        if self.data["user_id"] in data:
            self.data.update(data[self.data["user_id"]])

    def save_user_data(self):
        data_manager.save_data(self.data)

    def add_vice(self, vice_name):
        return self.habit_manager.add_habit(vice_name)

    def relapse_vice(self, vice_name):
        return self.habit_manager.relapse_habit(vice_name)

    def quit_vice(self, vice_name):
        return self.habit_manager.quit_habit(vice_name)

    def get_active_vices(self):
        return self.habit_manager.get_active_habits()

    def get_inactive_vices(self):
        return self.habit_manager.get_inactive_habits()
