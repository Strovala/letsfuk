import json
from functools import wraps


def check_memcache(**kwargs):
    def dec(func):
        @wraps(func)
        def wrapper(self, *args, **kw):
            if self.memcache is None:
                return
            return func(self, *args, **kw)
        return wrapper
    return dec


class Memcache(object):
    # Will be initialized in ioc after memcache is configured
    memcache = None

    @classmethod
    @check_memcache()
    def get_dict(cls, key):
        value = cls.memcache.get(key)
        if value is not None:
            return json.loads(value)
        return None

    @classmethod
    @check_memcache()
    def set_dict(cls, key, value):
        json_value = json.dumps(value)
        cls.memcache.set(key, json_value)

    @classmethod
    def get_or_set_dict(cls, key, callback, *args, **kwargs):
        value = cls.get_dict(key)
        if value is None:
            value = callback(*args, **kwargs)
            cls.set_dict(key, value)
        return value
