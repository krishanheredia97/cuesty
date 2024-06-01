from datetime import datetime, timezone
import random

class DifficultyLevel:
    def __init__(self, level, reward_config):
        self.level = int(level)  # Ensure level is always an integer
        self.xp_range = reward_config["difficulty_levels"][str(self.level)]["xp_range"]
        self.gp_range = reward_config["difficulty_levels"][str(self.level)]["gp_range"]
        self.honor_reward_range = reward_config["difficulty_levels"][str(self.level)]["honor_reward_range"]
        self.cost_range = reward_config["difficulty_levels"][str(self.level)]["honor_cost_range"]
        self.bonus_multipliers = reward_config["bonus_multipliers"]

    def get_base_xp(self, duration_weeks):
        return random.randint(self.xp_range[0], self.xp_range[1]) * duration_weeks

    def get_base_gp(self, duration_weeks):
        return random.randint(self.gp_range[0], self.gp_range[1]) * duration_weeks

    def get_base_honor(self, duration_weeks):
        return random.randint(self.honor_reward_range[0], self.honor_reward_range[1]) * duration_weeks

    def get_cost(self, duration_weeks):
        return random.randint(self.cost_range[0], self.cost_range[1]) * duration_weeks

    def apply_bonus(self, base_value, tier):
        if tier in self.bonus_multipliers:
            multiplier = self.bonus_multipliers[tier]
            base_value += int(base_value * multiplier)
        return base_value

class Quest:
    def __init__(self, quest_id, creator_name, reward_config, quest_status="draft", quest_name=None, quest_real_goal=None,
                 quest_difficulty=None, quest_type=None, quest_daily_instances=1, quest_fict_goal=None,
                 quest_stage=None, quest_enemy=None, quest_cutscene=None, quest_duration_cat=None,
                 quest_duration_num=None, quest_duration_weeks=None, quest_item_reward=None,
                 quest_creator=None, quest_participants=None, quest_enrolled_users=None, quest_validator=None,
                 quest_total_users=0, quest_daily_perfect_count=None, quest_overall_perfect_count=None,
                 quest_users_success_count=None, quest_users_failure_count=None, quest_users_unreported_count=None,
                 quest_current_day=None, quest_current_instance=None, quest_daily_success_rate=None,
                 quest_overall_success_rate=None, timestamp=None):
        self.quest_id = quest_id
        self.quest_status = quest_status
        self.quest_name = quest_name
        self.quest_real_goal = quest_real_goal
        self.quest_difficulty = int(quest_difficulty) if quest_difficulty is not None else None
        self.quest_type = quest_type
        self.quest_daily_instances = quest_daily_instances
        self.quest_fict_goal = quest_fict_goal
        self.quest_stage = quest_stage
        self.quest_enemy = quest_enemy if quest_enemy is not None else []
        self.quest_cutscene = quest_cutscene
        self.quest_duration_cat = quest_duration_cat
        self.quest_duration_num = quest_duration_num
        self.quest_duration_weeks = quest_duration_weeks
        self.quest_item_reward = quest_item_reward
        self.quest_creator = creator_name
        self.quest_participants = quest_participants if quest_participants is not None else []
        self.quest_enrolled_users = quest_enrolled_users if quest_enrolled_users is not None else []
        self.quest_validator = quest_validator
        self.quest_total_users = quest_total_users
        self.quest_daily_perfect_count = quest_daily_perfect_count
        self.quest_overall_perfect_count = quest_overall_perfect_count
        self.quest_users_success_count = quest_users_success_count
        self.quest_users_failure_count = quest_users_failure_count
        self.quest_users_unreported_count = quest_users_unreported_count
        self.quest_current_day = quest_current_day
        self.quest_current_instance = quest_current_instance
        self.quest_daily_success_rate = quest_daily_success_rate
        self.quest_overall_success_rate = quest_overall_success_rate
        self.timestamp = timestamp if timestamp else datetime.now(timezone.utc).isoformat()

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