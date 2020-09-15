from fastapi.testclient import TestClient

from CTFe.main import app
from CTFe.config import constants
from CTFe.models import *
from CTFe.config.database import (
    dal,
    Base,
)

dal.db_url = f"{constants.DB_TYPE}://{constants.TEST_DB_USERNAME}:{constants.TEST_DB_PASSWORD}@{constants.TEST_DB_ADDRESS}:{constants.TEST_DB_PORT}/{constants.TEST_DB_NAME}"

dal.init()

Base.metadata.drop_all(dal.engine)
Base.metadata.create_all(dal.engine)

# Create user
with dal.get_session_ctx() as session:
    user = User(username="client1", password="secret")

    session.add(user)
    session.commit()

client = TestClient(app)
