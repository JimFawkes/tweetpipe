"""
Database models representing the different tables in the DB.

Use the django ORM for its simplicity and the bundled schema migrations.

Second draft modeling the relevant data.
"""
from django.db import models


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    screen_name = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField()
    followers_count = models.PositiveIntegerField()
    # NOTE: Following
    friends_count = models.PositiveIntegerField()
    favourites_count = models.PositiveIntegerField()

    fetched_at = models.DateTimeField()

    class Meta:
        app_label = "tweetpipe"

    def __repr__(self):
        return f"User(id={self.id}, screen_name={self.screen_name}, created_at={self.created_at})"

    def __str__(self):
        return self.__repr__()


class Tweet(models.Model):
    id = models.BigIntegerField(primary_key=True)
    created_at = models.DateTimeField()
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="tweets"
    )
    # The full text may contain retweet information, the tweet itself and a url to the tweet.
    full_text = models.CharField(max_length=660)
    retweet_count = models.PositiveIntegerField()
    favorite_count = models.PositiveIntegerField()

    fetched_at = models.DateTimeField()

    tweet_url = models.URLField()
    # Note: It is possible for a tweet to have more than 280c. This may happen if unicode escapec codes are used.
    text = models.CharField(max_length=560)

    class Meta:
        app_label = "tweetpipe"

    def __repr__(self):
        return f"Tweet(id={self.id}, user={self.user}, created_at={self.created_at})"

    def __str__(self):
        return self.__repr__()


class AbstractCountModel(models.Model):
    count = models.IntegerField()
    fetched_at = models.DateTimeField()

    class Meta:
        abstract = True


class FollowerCount(AbstractCountModel):
    req_fields = ("user", "fetched_at")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower_counts"
    )

    class Meta:
        app_label = "tweetpipe"


class Hashtag(models.Model):
    req_fields = ("text",)
    text = models.CharField(max_length=279)
    tweets = models.ManyToManyField(Tweet, related_name="hashtags")

    class Meta:
        app_label = "tweetpipe"
