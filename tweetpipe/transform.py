"""
Transform the raw, extracted data.

The machinery for the ModelParser can be found in core.py

The top-level parser (TweetPipeParser) iterates through the tweets and passes
the tweet dict to all individual parsers
ObjParsers take the entire tweetdict (incl. tweetpipe_metadata) and do the following:
  - create artificial fields
  - reformat/filter dict to only contain relevant fields
  - return dict {model_class: fields}
TweetPipeParser then merges these dicts and returns a single dict.

"""
from loguru import logger

import utils
from core import ModelParser
from models import FollowerCount, Hashtag, Tweet, User

_log_file_name = __file__.split("/")[-1].split(".")[0]
logger.add(f"logs/tweetpipe_{_log_file_name}.log", rotation="1 day")


class TweetPipeParser:
    def __init__(self, data):
        self.raw_tweets = data.pop("tweets")
        # This could be moved into a registered decorator
        self.registered_parsers = [
            UserParser,
            TweetParser,
            FollowerCountParser,
            HashtagParser,
        ]

    def process(self):
        """Process the raw data and pass chunks onto the corresponding ModelParsers"""
        clean_user = {}
        for idx, raw_tweet in enumerate(self.raw_tweets):
            transformed_tweet = {}
            logger.debug(f"Start processing tweet idx={idx}")
            for model_parser in self.registered_parsers:
                # NOTE: This will parse user data for every tweet
                parser = model_parser(data=raw_tweet)
                parsed_data = parser.process()
                transformed_tweet = {**transformed_tweet, **parsed_data}

            yield transformed_tweet


class BaseModelParser(ModelParser):
    """Define all transformations that need to be done on all ModelParsers"""

    def __init__(self):
        super().__init__()
        self.relevant_fields = ["tweetpipe_metadata.*"] + self.relevant_fields
        self.field_transformations = {
            **{"fetched_at": self.transform_datetime},
            **self.field_transformations,
        }

    def transform_datetime(self, datetime_str):
        return utils.twitter_time_to_datetime(datetime_str)


class UserParser(BaseModelParser):
    def __init__(self, data):
        self.data = data
        self._model = User
        self.relevant_fields = ["user.*"]

        self.field_transformations = {"created_at": self.transform_datetime}

        super().__init__()


class FollowerCountParser(BaseModelParser):
    def __init__(self, data):
        self.data = data
        self._model = FollowerCount
        self.relevant_fields = ["user.followers_count", "user"]
        self.general_transformations = [self.transform_followers_count]

        super().__init__()

    def transform_followers_count(self):
        self.data["count"] = self.data["followers_count"]


class TweetParser(BaseModelParser):
    def __init__(self, data):
        self.data = data
        self._model = Tweet
        self.relevant_fields = ["*"]

        self.field_transformations = {"created_at": self.transform_datetime}

        self.general_transformations = [self.transform_full_text]
        super().__init__()

    def transform_full_text(self):
        full_text = self.data["full_text"]
        text_range = self.data["display_text_range"]
        text = str(full_text[text_range[0] : text_range[1]])
        tweet_url = str(full_text[text_range[1] + 1 :])
        self.data["text"] = text
        self.data["tweet_url"] = tweet_url


class HashtagParser(BaseModelParser):
    def __init__(self, data):
        self.data = data
        self._model = Hashtag
        self.relevant_fields = ["entities.hashtags"]
        super().__init__()

    def process(self):
        self.pre_transformation_filter()
        hashtags = []
        for hashtag in self.data["hashtags"]:
            fields = {"text": hashtag["text"], "tweet": None}
            # Hack
            fields["tweets"] = fields["tweet"]
            hashtags.append(fields)

        return {self._model: hashtags}


def get_transformed_data(data):
    """Entry function to run the main TweetPipeParser and transform the raw data"""
    parser = TweetPipeParser(data)
    return parser.process()
