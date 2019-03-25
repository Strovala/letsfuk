from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


def configuration(binder):
    connection = "postgresql://letsfuk:root@localhost/letsfuk"
    engine = create_engine(connection)
    session_class = scoped_session(sessionmaker(bind=engine))
    binder.bind_to_provider('db', session_class)
