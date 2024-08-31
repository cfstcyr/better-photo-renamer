def hash_dict(d: dict) -> int:
    return hash(frozenset(d.items()))


def hash_to_str(h: int) -> str:
    return str(hex(h))[2:][::-1].upper()
