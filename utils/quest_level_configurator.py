import json
from utils.random_number_picker import pick_random_number


def configure_level_requirements(difficulty_level, config_path='config/quest_default_config.json'):
    """
    Configure level-related requirements based on the difficulty level.

    :param difficulty_level: The difficulty level of the quest.
    :param config_path: Path to the configuration JSON file.
    :return: A dictionary with the minimum level requirement and thresholds.
    """
    with open(config_path, 'r') as file:
        config = json.load(file)

    difficulty_levels = config['difficulty_levels']

    if str(difficulty_level) in difficulty_levels:
        level_config = difficulty_levels[str(difficulty_level)]

        honor_cost = pick_random_number(level_config['honor_cost_range'])

        return {
            'quest_minimum_level_requirement': level_config['quest_minimum_level_requirement'],
            'honor_cost': honor_cost,
            'quest_yellow_threshold': level_config['quest_yellow_threshold'],
            'quest_green_threshold': level_config['quest_green_threshold'],
            'quest_cyan_threshold': level_config['quest_cyan_threshold']
        }
    else:
        raise ValueError("Invalid difficulty level")
