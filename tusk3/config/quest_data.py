from datetime import datetime, timezone
from utils.generate_unique_id import generate_unique_id


def get_initial_quest_data(creator):
    quest_id = generate_unique_id()
    timestamp = datetime.now(timezone.utc).isoformat()

    return {
        "Quest_Main": {
            "quest_id": quest_id,
            "timestamp": timestamp,
            "quest_status": "draft",
            "quest_name": None,
            "quest_real_goal": None,
            "quest_difficulty": None,
            "quest_type": None,
            "quest_daily_instances": 1
        },
        "Quest_Narrative": {
            "quest_fict_goal": None,
            "quest_stage": None,
            "quest_enemy": None,
            "quest_cutscene": None
        },
        "Quest_Time": {
            "quest_duration_cat": None,
            "quest_duration_num": None,
            "quest_duration_days": None,
            "quest_start_date": None,
            "quest_end_date": None,
            "quest_completion_time": None
        },
        "Quest_Rewards": {
            "quest_xp_reward": None,
            "quest_gp_reward": None,
            "quest_honor_reward": None,
            "quest_item_reward": None
        },
        "Quest_Users": {
            "quest_creator": creator,
            "quest_participants": [],
            "quest_enrolled_users": [],
            "quest_validator": None,
            "quest_total_users": None
        },
        "Quest_Requirements": {
            "quest_minimum_level_requirement": None,
            "quest_honor_cost": None,
            "quest_item_requirement": None,
            "quest_minimum_enrolled_users": None,
            "quest_type": "group"
        },
        "Quest_Progress": {
            "quest_daily_perfect_count": None,
            "quest_overall_perfect_count": None,
            "quest_users_success_count": None,
            "quest_users_failure_count": None,
            "quest_users_unreported_count": None,
            "quest_current_day": None,
            "quest_current_instance": None,
            "quest_daily_success_rate": None,
            "quest_overall_success_rate": None,
            "quest_yellow_threshold": None,
            "quest_green_threshold": None,
            "quest_cyan_threshold": None
        }
    }
