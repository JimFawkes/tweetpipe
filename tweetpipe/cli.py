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
from storage import S3, LocalFileSystem
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
STORAGE_CHOICES = {"s3": S3, "local": LocalFileSystem}

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
    "--count",
    "-c",
    help="nuber of recent tweets to retrieve",
    type=int,
    default=5,
)

parser.add_argument(
    "--list",
    "-l",
    action="store_true",
    help="list all files stored in the specified storage location (default: S3)",
)

parser.add_argument(
    "--storage",
    "-s",
    default=STORAGE_CHOICES[settings.DEFAULT_STORAGE_SYSTEM],
    nargs="?",
    choices=STORAGE_CHOICES,
    help=f"select a storage location for raw data (default: {settings.DEFAULT_STORAGE_SYSTEM})",
)

parser.add_argument(
    "--rerun_file",
    help="re-process and store data from a file stored in S3",
    type=str,
)

# Do not upload fetched tweets to s3
# parser.add_argument("--avoid_s3", action="store_true", help="Do not upload to S3")

# Should the transformation phase load old tweets from S3 instead of fetching new ones
# parser.add_argument("--read_from_s3", help="Read data from local file, clean, validate and store the data.", type=str)


def list_files(username, storage_system):
    """
    List all files stored in S3 for a given username.

    If the username is omitted, list all files in the S3 bucket.
    """
    logger.debug(f"List files for {username}")
    storage = storage_system()
    username, key_count, keys = storage.list(username)
    print("\n###############################################")
    print(f"Found {key_count} file(s) for username: {username}")
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


def extract(userhandle, count, storage_system):
    """Fetch tweets from api, convert it to json, and store it"""
    json_tweets = get_tweet_data(userhandle, count, storage_system)
    return json_tweets


def rerun_pipeline(filename, storage_system):
    """
    Run pipelien using previously fetched data

    Read content of a file with filename stored
    and continue with the transformation phase.
    """
    logger.debug(f"Rerun data from file: {filename}")
    storage = storage_system()
    json_tweets = storage.read(filename)
    transformed_data = transform(json_tweets)
    results = load(transformed_data)


def run_pipeline(userhandle, count, storage_system):
    """Run the entire Extract, Transform and Load Pipeline"""
    logger.debug(f"Extract last {count} tweets for '{userhandle}'")
    json_tweets = extract(userhandle, count, storage_system)
    transformed_data = transform(json_tweets)
    results = load(transformed_data)


def main():
    args = parser.parse_args()
    logger.debug(f"Starting TweetPipe")
    storage_system = STORAGE_CHOICES[args.storage]

    if args.list:
        username = args.user_handle or ""
        logger.debug(f"Username:{username}")
        list_files(username, storage_system)
    elif args.rerun_file:
        rerun_pipeline(args.rerun_file, storage_system)
    elif args.user_handle:
        run_pipeline(args.user_handle, args.count, storage_system)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
    sys.exit(0)
