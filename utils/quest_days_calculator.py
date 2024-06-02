DURATION_MULTIPLIERS = {
    'd': 1,
    'w': 7,
    'm': 30,
    'y': 365
}


def calculate_duration_days(duration_cat, duration_num):
    """
    Calculate the number of days based on the duration category and number.

    :param duration_cat: The duration category (d, w, m, y).
    :param duration_num: The number associated with the duration category.
    :return: The calculated number of days.
    """
    if duration_cat not in DURATION_MULTIPLIERS:
        raise ValueError("Invalid duration category")

    return DURATION_MULTIPLIERS[duration_cat] * duration_num
