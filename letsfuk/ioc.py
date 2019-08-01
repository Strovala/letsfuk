from pymemcache.client import base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import testing.postgresql

from letsfuk.cache import Memcache
from letsfuk.config import Config


def configuration(binder):
    config = Config("letsfuk.yaml")
    connection = config.get('database_url')
    engine = create_engine(connection)
    session_class = scoped_session(sessionmaker(bind=engine))
    cache = base.Client(('localhost', 11211))
    Memcache.memcache = cache
    binder.bind('cache', cache)
    binder.bind_to_provider('db', session_class)
    binder.bind(Config, config)
    binder.bind('db_engine', engine)


def testing_configuration(binder):
    config = Config("letsfuk-testing.yaml")
    postgres = testing.postgresql.Postgresql(
        initdb_args='-E=UTF8 -U postgres -A trust',
        port=5432
    )
    connection = postgres.url()
    engine = create_engine(connection)
    session_class = scoped_session(sessionmaker(bind=engine))
    binder.bind_to_provider('db', session_class)
    binder.bind(Config, config)
    binder.bind('db_engine', engine)
