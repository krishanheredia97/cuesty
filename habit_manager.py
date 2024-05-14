from habit import Habit
import data_manager

class HabitManager:
    def __init__(self, user_data):
        self.user_data = user_data
        self.user_data["vices"] = [Habit.from_dict(h) if isinstance(h, dict) else h for h in self.user_data["vices"]]

    def add_habit(self, habit_name):
        habit_name = habit_name.capitalize()
        if any(habit.name == habit_name for habit in self.user_data["vices"]):
            return False, f"'{habit_name}' already exists."
        new_habit = Habit(habit_name)
        self.user_data["vices"].append(new_habit)
        self.user_data["global_quit_count"] += 1
        self.save_user_data()
        return True, f"'{habit_name}' has been added to your vices!"

    def relapse_habit(self, habit_name):
        for habit in self.user_data["vices"]:
            if habit.name == habit_name and habit.status == "Active":
                habit.relapse()
                self.user_data["global_relapse_count"] += 1
                self.save_user_data()
                return True, f"You have relapsed on '{habit_name}'."
        return False, f"'{habit_name}' is not an active vice."

    def quit_habit(self, habit_name):
        for habit in self.user_data["vices"]:
            if habit.name == habit_name and habit.status == "Inactive":
                habit.quit()
                self.user_data["global_quit_count"] += 1
                self.save_user_data()
                return True, f"You have quit '{habit_name}'."
        return False, f"'{habit_name}' is not an inactive vice."

    def get_active_habits(self):
        return [habit.name for habit in self.user_data["vices"] if habit.status == "Active"]

    def get_inactive_habits(self):
        return [habit.name for habit in self.user_data["vices"] if habit.status == "Inactive"]

    def save_user_data(self):
        self.user_data["vices"] = [habit.to_dict() for habit in self.user_data["vices"]]
        data_manager.save_data(self.user_data)
