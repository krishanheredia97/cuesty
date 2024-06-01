import json
from utils.random_number_picker import pick_random_number


def calculate_rewards(difficulty_level, config_path='config/quest_default_config.json'):
    """
    Calculate the rewards based on the difficulty level.

    :param difficulty_level: The difficulty level of the quest.
    :param config_path: Path to the configuration JSON file.
    :return: A dictionary with the calculated XP reward, GP reward, and Honor reward.
    """
    with open(config_path, 'r') as file:
        config = json.load(file)

    difficulty_levels = config['difficulty_levels']

    if str(difficulty_level) in difficulty_levels:
        level_config = difficulty_levels[str(difficulty_level)]

        xp_reward = pick_random_number(level_config['xp_range'])
        gp_reward = pick_random_number(level_config['gp_range'])
        honor_reward = pick_random_number(level_config['honor_reward_range'])

        return {
            'xp_reward': xp_reward,
            'gp_reward': gp_reward,
            'honor_reward': honor_reward
        }
    else:
        raise ValueError("Invalid difficulty level")
