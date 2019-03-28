from tornado_sqlalchemy import declarative_base
from sqlalchemy.exc import IntegrityError


Base = declarative_base()


def commit(db):
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise e
