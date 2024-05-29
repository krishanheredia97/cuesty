import random

class DifficultyLevel:
    def __init__(self, level, reward_config):
        self.level = level
        self.xp_range = reward_config["difficulty_levels"][str(level)]["xp_range"]
        self.gp_range = reward_config["difficulty_levels"][str(level)]["gp_range"]
        self.honor_range = reward_config["difficulty_levels"][str(level)]["honor_reward_range"]
        self.cost_range = reward_config["difficulty_levels"][str(level)]["honor_cost_range"]
        self.bonus_multipliers = reward_config["bonus_multipliers"]

    def get_base_xp(self, duration_weeks):
        return random.randint(self.xp_range[0], self.xp_range[1]) * duration_weeks

    def get_base_gp(self, duration_weeks):
        return random.randint(self.gp_range[0], self.gp_range[1]) * duration_weeks

    def get_base_honor(self, duration_weeks):
        return random.randint(self.honor_range[0], self.honor_range[1]) * duration_weeks

    def get_cost(self, duration_weeks):
        return random.randint(self.cost_range[0], self.cost_range[1]) * duration_weeks

    def apply_bonus(self, base_value, tier):
        if tier in self.bonus_multipliers:
            multiplier = self.bonus_multipliers[tier]
            base_value += int(base_value * multiplier)
        return base_value


class Quest:
    def __init__(self, quest_id, quest_name, quest_real_goal, quest_fict_goal, quest_cutscene, quest_stage,
                 quest_item_reward, quest_duration_weeks, quest_enemy, quest_difficulty, reward_config):
        self.quest_id = quest_id
        self.quest_name = quest_name
        self.quest_real_goal = quest_real_goal
        self.quest_fict_goal = quest_fict_goal
        self.quest_cutscene = quest_cutscene
        self.quest_stage = quest_stage
        self.quest_item_reward = quest_item_reward
        self.quest_duration_weeks = quest_duration_weeks
        self.quest_enemy = quest_enemy
        self.quest_difficulty = quest_difficulty
        self.reward_config = reward_config

    def calculate_rewards(self, tier='yellow'):
        difficulty = DifficultyLevel(self.quest_difficulty, self.reward_config)
        base_xp = difficulty.get_base_xp(self.quest_duration_weeks)
        base_gp = difficulty.get_base_gp(self.quest_duration_weeks)
        base_honor = difficulty.get_base_honor(self.quest_duration_weeks)

        final_xp = difficulty.apply_bonus(base_xp, tier)
        final_gp = difficulty.apply_bonus(base_gp, tier)
        final_honor = difficulty.apply_bonus(base_honor, tier)

        return final_xp, final_gp, final_honor

    def calculate_cost(self):
        difficulty = DifficultyLevel(self.quest_difficulty, self.reward_config)
        return difficulty.get_cost(self.quest_duration_weeks)
