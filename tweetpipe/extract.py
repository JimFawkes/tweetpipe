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
    def __init__(self, username, count):
        self._tweet_mode = "extended"
        self._json_indent = 2  # Might want to move this to settings
        self._api = self._auth()

        self.username = username
        self.count = count
        self.user = self.get_user()

        self._s3 = self._s3_client()

    def _auth(self):
        """Authenticate with Twitter and return a tweepy API inst."""

        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET_KEY)
        auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_SECRET_ACCESS_TOKEN)

        return tweepy.API(auth)

    def _s3_client(self):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )
        return s3

    def get_user(self):
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
        fetched_tweets = {
            "fetched_at": utils.datetime_to_twitter_format(self.fetched_at),
            "username": self.username,
            "count": self.count,
            "tweets": [],
        }
        for tweet in self.tweets:
            fetched_tweets["tweets"].append(tweet._json)

        fetched_tweets = json.dumps(fetched_tweets, indent=self._json_indent)

        self.json_tweets = fetched_tweets
        return fetched_tweets

    def upload_json_to_s3(self):
        """Upload raw unformatted tweet data to S3 Bucket"""
        key = f"{self.username}/{utils.datetime_to_string_format(self.fetched_at)}.json"
        response = self._s3.put_object(Bucket=settings.AWS_BUCKET_NAME, Body=self.json_tweets, Key=key)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            logger.info(response)
            return None
        else:
            logger.warning(response)
            return response


def get_tweet_data(username, count, upload_to_s3=True):
    tweets = Tweets(username=username, count=count)
    tweets.fetch()
    json_tweets = tweets.convert_tweets_to_json()
    if upload_to_s3:
        response = tweets.upload_json_to_s3()
    return json_tweets
