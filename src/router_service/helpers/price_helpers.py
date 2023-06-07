"""
Price helpers.
"""


def to_int_percent(value: float):
    """
    Convert the given float to an integer representation of the value as a percentage.

    :param value: The float (eg 0.2 or 1.35)
    :return: Its integer representation (eg 20 or 135)
    """
    if value < 1:
        return int(value * 100)
    return int(value * 100) - 100


def int_to_percent_increase_multiplier(value: int):
    """
    Convert integer values to float multipliers.

    :param value: Integer (eg 20)
    :return: Float representation of int + 100 (eg 120)
    """
    return (value + 100) / 100.0


def get_price_mod_for(item, lookup, default=0):
    """
    Get the price modifier for the given item or sequence by fetching modifiers for all values and averaging those.

    :param item: Item or list of modifier names
    :param lookup: Lookup for the given modifier type
    :param default: Value to use if an item isn't in the lookup
    :return: Average of modifier values
    """
    if type(item) is not list:
        item = [item]
    types = [lookup.get(item, default) for item in item]
    return sum(types) / len(types)
