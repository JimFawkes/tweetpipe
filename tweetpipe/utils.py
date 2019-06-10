from datetime import datetime
from config import settings


def datetime_to_twitter_format(raw_datetime):
    return datetime.strftime(raw_datetime, settings.TWITTER_TIME_FORMAT)


def twitter_time_to_datetime(formatted_datetime):
    return datetime.strptime(formatted_datetime, settings.TWITTER_TIME_FORMAT)


def datetime_to_string_format(raw_datetime):
    return datetime.strftime(raw_datetime, settings.TIME_STRING_FORMAT)
