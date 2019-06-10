"""CLI to run base tweetpipe

"""

import argparse
import sys
from loguru import logger

from config import settings
from extract import get_tweet_data

# from config import Config

_log_file_name = __file__.split("/")[-1].split(".")[0]
logger.add(f"logs/tweetpipe_{_log_file_name}.log", rotation="1 day")

# config = Config()

help_text = """
Project TweetPipe - A Contentful Challenge

"""

epilog = """

Written as first draft by Moritz Eilfort.

"""

parser = argparse.ArgumentParser(
    prog="tweetpipe", formatter_class=argparse.RawDescriptionHelpFormatter, description=help_text, epilog=epilog
)

parser.add_argument("--user_handle", "-u", help="Twitter User Handle (@'handle')", type=str, required=True)

parser.add_argument("--count", "-c", help="Nuber of recent tweets to retrieve", type=int, default=5)

# Do not upload fetched tweets to s3
# parser.add_argument("--avoid_s3", action="store_true", help="Do not upload to S3")

# Should the transformation phase load old tweets from S3 instead of fetching new ones
# parser.add_argument("--read_from_s3", help="Read data from local file, clean, validate and store the data.", type=str)


def extract(userhandle, count, upload_to_s3=True):
    """Fetch tweets from api, convert it to json, upload to s3"""
    json_tweets = get_tweet_data(userhandle, count, upload_to_s3)
    return json_tweets


def run_pipeline(userhandle, count):
    logger.debug(f"Extract last {count} tweets for '{userhandle}'")
    json_tweets = extract(userhandle, count)


def main():
    args = parser.parse_args()
    logger.debug(f"Starting TweetPipe")

    run_pipeline(str(args.user_handle), int(args.count))


if __name__ == "__main__":
    main()
