import json


class Memcache(object):
    # Will be initialized in ioc after memcache is configured
    memcache = None

    @classmethod
    def get_dict(cls, key):
        value = cls.memcache.get(key)
        if value is not None:
            return json.loads(value)
        return None

    @classmethod
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
