"""
Utilities for Project TweetPipe.
"""
from datetime import datetime
from config import settings


# Timeformat conversions
def datetime_to_twitter_format(raw_datetime):
    return datetime.strftime(raw_datetime, settings.TWITTER_TIME_FORMAT)


def twitter_time_to_datetime(formatted_datetime):
    return datetime.strptime(formatted_datetime, settings.TWITTER_TIME_FORMAT)


def datetime_to_string_format(raw_datetime):
    return datetime.strftime(raw_datetime, settings.TIME_STRING_FORMAT)


def convert_datetime_format_str(from_format, to_format, datetime_str):
    return datetime.strptime(datetime_str, from_format).strftime(to_format)


def convert_twitter2default_format(datetime_str):
    return convert_datetime_format_str(settings.TWITTER_TIME_FORMAT, settings.DEFAULT_DATETIME_FORMAT, datetime_str)


def filter_dict(bigdict, fields):
    """Shrink a big dict to only contain keys in fields"""
    fields = set(fields)
    return {k: bigdict[k] for k in bigdict.keys() & fields}
