from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()


# Raise error if a value is None
# -------------------------------
none_value_error = (
    lambda value_name:
        ValueError(f"Value for { value_name } can not equal None")
)


# Application specific configs
# -----------------------------
MAX_TEAM_MEMBERS = 5


# DB related configs
# -------------------
DB_TYPE = os.getenv("DB_TYPE")

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_ADDRESS = os.getenv("DB_ADDRESS")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

TEST_DB_USERNAME = os.getenv("TEST_DB_USERNAME")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD")
TEST_DB_ADDRESS = os.getenv("TEST_DB_ADDRESS")
TEST_DB_PORT = os.getenv("TEST_DB_PORT")
TEST_DB_NAME = os.getenv("TEST_DB_NAME")

if DB_TYPE is None:
    raise none_value_error("DB_TYPE")

if DB_USERNAME is None:
    raise none_value_error("DB_USERNAME")
if DB_PASSWORD is None:
    raise none_value_error("DB_PASSWORD")
if DB_ADDRESS is None:
    raise none_value_error("DB_ADDRESS")
if DB_PORT is None:
    raise none_value_error("DB_PORT")
if DB_NAME is None:
    raise none_value_error("DB_NAME")


# Redis related configs
# ----------------------
REDIS_EXPIRE = 1 * 60   # Calculated in seconds (e.g. 2 * 60 => 2 minutes)

REDIS_ADDRESS = f"redis://{os.getenv('REDIS_ADDRESS')}"
REDIS_DB_NAME = os.getenv("REDIS_DB_NAME")
try:
    REDIS_DB_NAME = int(REDIS_DB_NAME)
except:
    raise

TEST_REDIS_ADDRESS = f"redis://{os.getenv('TEST_REDIS_ADDRESS')}"
TEST_REDIS_DB_NAME = os.getenv("TEST_REDIS_DB_NAME")
try:
    TEST_REDIS_DB_NAME = int(TEST_REDIS_DB_NAME)
except:
    raise


if REDIS_ADDRESS is None:
    raise none_value_error("REDIS_ADDRESS")
if REDIS_DB_NAME is None:
    raise none_value_error("REDIS_DB_NAME")

# JWT related configs
# --------------------
JWT_ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRE_TIME = 15    # It's in minutes (e.g. 15 => 15 minutes)

if JWT_SECRET is None:
    raise none_value_error("JWT_SECRET")


# Auth Token configs
# -------------------
# X_TOKEN = "X-Token"
