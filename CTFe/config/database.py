from sqlalchemy.ext.declarative import declarative_base


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

    def init_session(self):
        self.engine = create_engine(self.db_url)
        self._SessionLocal = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )

    def get_session(self):
        if self.engine is None:
            self.init_session()

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