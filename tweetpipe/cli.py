"""CLI to run tweetpipe

"""
import argparse
import django
import os
import sys
from loguru import logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# Necessary for the ORM to work
django.setup()

from config import settings
from extract import get_tweet_data
from load import load_data
from storage import S3
from transform import get_transformed_data

_log_file_name = __file__.split("/")[-1].split(".")[0]
logger.add(f"logs/tweetpipe_{_log_file_name}.log", rotation="1 day")


help_text = """
Project TweetPipe - A Contentful Challenge

Retrieve twitter data for a given username, transform the data 
and store it in a DB.

The steps are:
    1) Get last 'count' tweets of user ('user_handle')
    2) Store the data along with metadata in an S3 Bucket
    3) Transform the raw data
    4) Store transformed data in the DB

In addition to the base process, it is also possible to list all files stored in S3 and to
re-run the pipeline using the data in S3 instead of newly fetched data.

"""

epilog = """

Written as first draft by Moritz Eilfort.

"""

parser = argparse.ArgumentParser(
    prog="tweetpipe",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=help_text,
    epilog=epilog,
)

parser.add_argument(
    "--user_handle", "-u", help="twitter user handle (@'handle')", type=str
)

parser.add_argument(
    "--count", "-c", help="nuber of recent tweets to retrieve", type=int, default=5
)

parser.add_argument(
    "--list",
    "-l",
    action="store_true",
    help="list all retrieved files stored in S3 for a given username",
)

parser.add_argument(
    "--rerun_file", help="re-process and store data from a file stored in S3", type=str
)

# Do not upload fetched tweets to s3
# parser.add_argument("--avoid_s3", action="store_true", help="Do not upload to S3")

# Should the transformation phase load old tweets from S3 instead of fetching new ones
# parser.add_argument("--read_from_s3", help="Read data from local file, clean, validate and store the data.", type=str)


def list_files(username):
    """
    List all files stored in S3 for a given username.

    If the username is omitted, list all files in the S3 bucket.
    """
    logger.debug(f"List files for {username}")
    s3 = S3()
    username, key_count, keys = s3.list(username)
    print("\n###############################################")
    print(f"Found {key_count} files for username: {username}")
    print("###############################################\n")
    for key in keys:
        print(key)

    print("\n###############################################\n")


def load(transformed_data):
    """Store transformed_data in the DB"""
    result = load_data(transformed_data)
    return result


def transform(json_data):
    """Transform raw data"""
    transformed_data = get_transformed_data(json_data)
    # logger.debug(list(transformed_data))
    return transformed_data


def extract(userhandle, count, upload_to_s3=True):
    """Fetch tweets from api, convert it to json, upload to s3"""
    json_tweets = get_tweet_data(userhandle, count, upload_to_s3)
    return json_tweets


def rerun_pipeline(filename):
    """
    Run pipelien using previously fetched data

    Read content of a file with filename stored in S3
    and continue with the transformation phase.
    """
    logger.debug(f"Rerun data from file: {filename}")
    s3 = S3()
    json_tweets = s3.read(filename)
    transformed_data = transform(json_tweets)
    results = load(transformed_data)


def run_pipeline(userhandle, count):
    """Run the entire Extract, Transform and Load Pipeline"""
    logger.debug(f"Extract last {count} tweets for '{userhandle}'")
    json_tweets = extract(userhandle, count)
    transformed_data = transform(json_tweets)
    results = load(transformed_data)


def main():
    args = parser.parse_args()
    logger.debug(f"Starting TweetPipe")

    if args.list:
        username = args.user_handle or ""
        logger.debug(f"Username:{username}")
        list_files(username)
    elif args.rerun_file:
        rerun_pipeline(str(args.rerun_file))
    elif args.user_handle:
        run_pipeline(args.user_handle, int(args.count))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
    sys.exit(0)
