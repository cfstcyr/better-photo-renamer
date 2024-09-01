import hashlib


def hash_dict(d: dict) -> str:
    m = hashlib.md5()

    for key, value in d.items():
        m.update(str(key).encode())
        m.update(":".encode())
        m.update(str(value).encode())
        m.update(";".encode())

    return m.hexdigest()
