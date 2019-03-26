import io
import os

import yaml

base_dir = os.path.dirname(os.path.realpath(__file__))


class Config(object):
    def __init__(self, file):
        path = os.path.join(base_dir, 'config', file)
        with io.open(path, 'r') as stream:
            try:
                self.data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc

    def get(self, key, default=None):
        return self.data.get(key, default)
