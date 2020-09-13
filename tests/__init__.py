from fastapi.testclient import TestClient

from CTFe.main import app
from CTFe.config import constants
from CTFe.config.database import dal

dal.db_url = f"{constants.DB_TYPE}://{constants.TEST_DB_USERNAME}:{constants.TEST_DB_PASSWORD}@{constants.TEST_DB_ADDRESS}:{constants.TEST_DB_PORT}/{constants.TEST_DB_NAME}"

client = TestClient(app)
