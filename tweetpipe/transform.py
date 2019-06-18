"""
Transform the raw, extracted/loaded data.

The TweetPipeParser takes the entire raw data and passes data chuncks to
the corresponding ModelParsers.

The machinery for the ModelParser can be found in core.py
"""
from loguru import logger

import utils
from core import ModelParser
from models import User, Tweet

_log_file_name = __file__.split("/")[-1].split(".")[0]
logger.add(f"logs/tweetpipe_{_log_file_name}.log", rotation="1 day")


class TweetPipeParser:
    def __init__(self, data):
        self.metadata = data.pop("metadata")
        self.raw_tweets = data.pop("tweets")

    def process(self):
        """Process the raw data and pass chuncks onto the corresponding ModelParsers"""
        clean_user = {}
        for idx, raw_tweet in enumerate(self.raw_tweets):
            user = raw_tweet.pop("user")
            if idx == 0:
                logger.debug(f"Start Processing a User")
                parsed_user = UserParser(data={**user, **self.metadata})
                clean_user = parsed_user.process()

            raw_tweet = {**raw_tweet, **clean_user}

            logger.debug(f"Processing Tweet idx={idx}")
            parsed_tweet = TweetParser(data={**raw_tweet, **self.metadata})
            clean_tweet = parsed_tweet.process()
            yield clean_tweet


class BaseModelParser(ModelParser):
    """Define all transformations that need to be done on all ModelParsers"""

    def __init__(self):
        super().__init__()
        self.field_transformations = {
            **{
                "created_at": self.transform_datetime,
                "fetched_at": self.transform_datetime,
            },
            **self.field_transformations,
        }

    def transform_datetime(self, datetime_str):
        return utils.twitter_time_to_datetime(datetime_str)


class UserParser(BaseModelParser):
    def __init__(self, data):
        self.data = data
        self._model = User

        super().__init__()


class TweetParser(BaseModelParser):
    def __init__(self, data):
        self.data = data
        self._model = Tweet

        self.field_transformations = {"full_text": self.transform_full_text}

        super().__init__()

    def transform_full_text(self, full_text):
        text_range = self.data["display_text_range"]
        text = str(full_text[text_range[0] : text_range[1]])
        tweet_url = str(full_text[text_range[1] + 1 :])
        self.data["text"] = text
        self.data["tweet_url"] = tweet_url
        return str(full_text)


def get_transformed_data(data):
    """Entry function to run the main TweetPipeParser and transform the raw data"""
    parser = TweetPipeParser(data)
    return parser.process()
