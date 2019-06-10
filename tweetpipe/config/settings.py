import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(".")
PROJECT_DIR = ROOT_DIR / "tweetpipe"
CONFIG_DIR = PROJECT_DIR / "config"
LOG_DIR = ROOT_DIR / "logs"
DATA_DIR = ROOT_DIR / "data"
TEST_DIR = ROOT_DIR / "tests"
ENV_PATH = CONFIG_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

# DJANGO
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
TIME_ZONE = "Europe/Berlin"
USE_TZ = True
TIME_STRING_FORMAT = "%Y%m%d-%H%M%S%z"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", default="tweetpipe"),
        "USER": os.getenv("DB_USER", default="tweetpipe_user"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", default="127.0.0.1"),
        "PORT": os.getenv("DB_PORT", default="5432"),
    }
}


# TWITTER
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET_KEY = os.getenv("TWITTER_CONSUMER_SECRET_KEY")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_SECRET_ACCESS_TOKEN = os.getenv("TWITTER_SECRET_ACCESS_TOKEN")
# Timeformat (Example: "Tue Jun 04 23:12:08 +0000 2019")
TWITTER_TIME_FORMAT = "%a %b %d %H:%M:%S %z %Y"

# AWS
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", default="tweetpipe")
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME", default="eu-central-1")
