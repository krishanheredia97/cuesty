import random


def pick_random_number(range_list):
    """
    Pick a random number within a given range.

    :param range_list: List containing two integers [min, max].
    :return: A random integer within the given range.
    """
    return random.randint(range_list[0], range_list[1])
