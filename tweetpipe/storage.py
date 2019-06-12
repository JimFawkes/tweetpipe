"""
Organize the interactions with AWS S3.

This is a simple abstraction layer over boto3's S3 client.
"""

import boto3
from loguru import logger

from config import settings


class S3:
    def __init__(self):
        self.region_name = settings.AWS_REGION_NAME
        self.bucket_name = settings.AWS_BUCKET_NAME
        self.name = "s3"

    @property
    def _client(self):
        client = boto3.client(
            self.name,
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=self.region_name,
        )
        return client

    def upload(self, filename, body):
        """Upload body to file with filename in S3 Bucket"""
        response = self._client.put_object(Bucket=self.bucket_name, Body=body, Key=filename)
        if not response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            logger.warning(response)
            return response

    def list(self, username=None):
        """List files with prefix username stored in S3"""
        response = self._client.list_objects_v2(Bucket=self.bucket_name, Prefix=username)
        key_count = response["KeyCount"]
        contents = response["Contents"]
        keys = [file["Key"] for file in contents]
        return username, key_count, keys

    def read(self, filename):
        """Read file content of file with certain filename"""
        response = self._client.get_object(Bucket=self.bucket_name, Key=filename)
        data = response["Body"].read()
        return data
