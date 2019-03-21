import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SESSION_TTL = 30
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=SESSION_TTL)
    SECRET_KEY = b'$\\m!\xab\xd6>\xa32\xe09\xf9_\x10\x81\xb9'
    SESSION_USE_SIGNER = True
    SESSION_TYPE = 'redis'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
