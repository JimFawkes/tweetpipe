"""
Extract tweets for a given user.

Use tweepy to interact with the twitter api.

After fetching the data, also upload the raw data along with metadata to S3,
incase the later steps need to be rerun at some point.
"""
import boto3
import tweepy
import json
from loguru import logger

from django.utils import timezone

from config import settings
import utils

# from config import Config
_log_file_name = __file__.split("/")[-1].split(".")[0]
logger.add(f"logs/tweetpipe_{_log_file_name}.log", rotation="1 day")


class Tweets:
    def __init__(self, username, count, storage_system):
        self._tweet_mode = "extended"
        self._json_indent = 2  # Might want to move this to settings
        self._api = self._auth()

        self.username = username
        self.count = count
        self.user = self.get_user()

        self.storage = storage_system()

    def _auth(self):
        """Authenticate with Twitter and return a tweepy API inst."""

        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET_KEY)
        auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_SECRET_ACCESS_TOKEN)

        return tweepy.API(auth)

    def get_user(self):
        """Get the user referenced by the username"""
        # TODO: Catch Unknown User Exception
        return self._api.get_user(self.username)

    @property
    def fetched(self):
        return hasattr(self, "fetched_at") and hasattr(self, "tweets")

    def fetch(self):
        """Fetch the 'count' most recent tweets for 'username'"""
        fetched_at = timezone.now()
        tweets = self.user.timeline(tweet_mode=self._tweet_mode, count=self.count)
        self.fetched_at = fetched_at
        self.tweets = tweets

    def convert_tweets_to_json(self):
        """Convert tweet data and metadata to json"""
        fetched_tweets = {
            "metadata": {
                "fetched_at": utils.datetime_to_twitter_format(self.fetched_at),
                "username": self.username,
                "count": self.count,
            },
            "tweets": [],
        }
        for tweet in self.tweets:
            fetched_tweets["tweets"].append(tweet._json)

        fetched_tweets = json.dumps(fetched_tweets, indent=self._json_indent)

        self.json_tweets = fetched_tweets
        return fetched_tweets

    @property
    def filename(self):
        return f"{self.username}/{utils.datetime_to_string_format(self.fetched_at)}.json"

    def write(self):
        """Convinience method wrapping storage.write"""
        logger.debug(f"Write tweets to storage with filename {self.filename}.")
        self.storage.write(self.filename, self.json_tweets)


def get_tweet_data(username, count, storage_system):
    """
    Entry function to extract count tweets from username

        username: str
        count: int
        storage: storage class (storage.[S3|LocalFileSystem])

    If storage is set, store the raw file with appended
    metadata.
    """
    tweets = Tweets(username=username, count=count, storage_system=storage_system)
    tweets.fetch()
    json_tweets = tweets.convert_tweets_to_json()
    if storage_system:
        tweets.write()
    return json_tweets
