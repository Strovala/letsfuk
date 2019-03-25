from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from config import Config


def configuration(binder):
    config = Config("letsfuk.yaml")
    connection = config.get('database_url')
    engine = create_engine(connection)
    session_class = scoped_session(sessionmaker(bind=engine))
    binder.bind_to_provider('db', session_class)
    binder.bind(Config, config)
