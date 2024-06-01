import json


def set_default_values(config_path='config/quest_default_config.json'):
    """
    Set default values for the quest.

    :param config_path: Path to the configuration JSON file.
    :return: A dictionary with the default values.
    """
    with open(config_path, 'r') as file:
        config = json.load(file)

    default_values = config['default_values']

    return {
        'quest_minimum_enrolled_users': default_values['quest_minimum_enrolled_users'],
        'quest_type': default_values['quest_type']
    }
