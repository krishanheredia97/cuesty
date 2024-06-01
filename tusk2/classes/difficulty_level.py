import random


class DifficultyLevel:
    def __init__(self, level, reward_config):
        self.level = level
        self.xp_range = reward_config["difficulty_levels"][str(level)]["xp_range"]
        self.gp_range = reward_config["difficulty_levels"][str(level)]["gp_range"]
        self.honor_reward_range = reward_config["difficulty_levels"][str(level)]["honor_reward_range"]
        self.cost_range = reward_config["difficulty_levels"][str(level)]["honor_cost_range"]
        self.bonus_multipliers = reward_config["bonus_multipliers"]

        print(f"Level: {level}")
        print(f"XP Range: {self.xp_range}")
        print(f"GP Range: {self.gp_range}")
        print(f"Honor Reward Range: {self.honor_reward_range}")
        print(f"Cost Range: {self.cost_range}")

    def get_base_xp(self, duration_weeks):
        base_xp = random.randint(self.xp_range[0], self.xp_range[1]) * duration_weeks
        print(f"Generated Base XP: {base_xp}")
        return base_xp

    def get_base_gp(self, duration_weeks):
        base_gp = random.randint(self.gp_range[0], self.gp_range[1]) * duration_weeks
        print(f"Generated Base GP: {base_gp}")
        return base_gp

    def get_base_honor(self, duration_weeks):
        base_honor = random.randint(self.honor_reward_range[0], self.honor_reward_range[1]) * duration_weeks
        print(f"Generated Base Honor: {base_honor}")
        return base_honor

    def get_cost(self, duration_weeks):
        cost = random.randint(self.cost_range[0], self.cost_range[1]) * duration_weeks
        print(f"Generated Cost: {cost}")
        return cost

    def apply_bonus(self, base_value, tier):
        if tier in self.bonus_multipliers:
            multiplier = self.bonus_multipliers[tier]
            base_value += int(base_value * multiplier)
        return base_value
