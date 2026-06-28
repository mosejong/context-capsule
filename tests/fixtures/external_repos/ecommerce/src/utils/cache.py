_cache = {}


def get_cache(key: str):
    return _cache.get(key)


def set_cache(key: str, value):
    _cache[key] = value
    return value
