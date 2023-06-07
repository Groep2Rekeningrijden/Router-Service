def to_int_percent(value: float):
    if value < 1:
        return int(value * 100)
    return int(value * 100) - 100


def int_to_percent(value: int):
    return (value + 100) / 100.0


def get_price_mod_for(seq, lookup, default=0):
    if type(seq) is not list:
        seq = [seq]
    types = [lookup.get(item, default) for item in seq]
    return sum(types) / len(types)
