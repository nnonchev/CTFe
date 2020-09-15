from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from CTFe.config import constants


# The model's base class configuration
# -------------------------------------
Base = declarative_base()


# DataAccessLayer class configuration
# ------------------------------------
class DataAccessLayer:
    def __init__(self):
        self.db_url: str = None

        self.engine = None
        self._SessionLocal = None

    def init(self):
        self.engine = create_engine(self.db_url)
        self._SessionLocal = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )

    def get_session(self):
        if self.engine is None:
            self.init()

        session = self._SessionLocal()

        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def get_session_ctx(self):
        if self.engine is None:
            self.init()

        session = self._SessionLocal()

        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()


dal = DataAccessLayer()
dal.db_url = f"{constants.DB_TYPE}://{constants.DB_USERNAME}:{constants.DB_PASSWORD}@{constants.DB_ADDRESS}:{constants.DB_PORT}/{constants.DB_NAME}"