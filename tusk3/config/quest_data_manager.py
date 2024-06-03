

QUEST_STRUCTURE = {
    "Quest_Main": [
        "quest_id", "timestamp", "quest_status", "quest_name", "quest_real_goal",
        "quest_difficulty", "quest_type", "quest_daily_instances"
    ],
    "Quest_Narrative": [
        "quest_fict_goal", "quest_stage", "quest_enemy", "quest_cutscene"
    ],
    "Quest_Time": [
        "quest_duration_cat", "quest_duration_num", "quest_duration_weeks",
        "quest_start_date", "quest_end_date", "quest_completion_time"
    ],
    "Quest_Rewards": [
        "quest_xp_reward", "quest_gp_reward", "quest_honor_reward", "quest_item_reward"
    ],
    "Quest_Users": [
        "quest_creator", "quest_participants", "quest_enrolled_users", "quest_validator", "quest_total_users"
    ],
    "Quest_Requirements": [
        "quest_minimum_level_requirement", "quest_honor_cost", "quest_item_requirement",
        "quest_minimum_enrolled_users", "quest_type"
    ],
    "Quest_Progress": [
        "quest_daily_perfect_count", "quest_overall_perfect_count", "quest_users_success_count",
        "quest_users_failure_count", "quest_users_unreported_count", "quest_current_day",
        "quest_current_instance", "quest_daily_success_rate", "quest_overall_success_rate",
        "quest_yellow_threshold", "quest_green_threshold", "quest_cyan_threshold"
    ]
}


def get_quest_item_path(item):
    """
    Determine the path of the given item based on the quest data structure.

    :param item: The item to find the path for.
    :return: The path string for the item.
    """
    for category, items in QUEST_STRUCTURE.items():
        if item in items:
            return f"{category}/{item}"
    return None
