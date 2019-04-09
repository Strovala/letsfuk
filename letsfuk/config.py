import io
import os

import yaml

app_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")


class Config(object):
    def __init__(self, file):
        path = os.path.join(app_dir, 'config', file)
        with io.open(path, 'r') as stream:
            try:
                self.data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        if key in self.data:
            self.data[key] = value
