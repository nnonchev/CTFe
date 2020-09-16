from fastapi.testclient import TestClient

# from CTFe.main import app
from CTFe.config import constants
from CTFe.models import *
from CTFe.config.database import (
    dal,
    Base,
)
from CTFe.utils.redis_utils import redis_dal

dal.db_url = f"{constants.DB_TYPE}://{constants.TEST_DB_USERNAME}:{constants.TEST_DB_PASSWORD}@{constants.TEST_DB_ADDRESS}:{constants.TEST_DB_PORT}/{constants.TEST_DB_NAME}"

dal.init()

Base.metadata.drop_all(dal.engine)
Base.metadata.create_all(dal.engine)

redis_dal.redis_url = constants.TEST_REDIS_ADDRESS
redis_dal.redis_db = constants.TEST_REDIS_DB_NAME

# client = TestClient(app)
