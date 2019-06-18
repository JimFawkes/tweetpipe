"""
Organize the interactions with AWS S3.

This is a simple abstraction layer over boto3's S3 client.
"""

import boto3
import json
from loguru import logger

from config import settings


class BaseStorage:
    """
    Base Class for all file storage systems.

    The api expects to get and returns python dictionaries.
    """

    def __init__(self):
        logger.info(f"Using {self.__class__.__name__} as storage")
        self.json_indent = 2

    def write(self, filename, data):
        raise NotImplementedError(
            f"{self.__class__.__name__}.write(filename, data) Not Implemented."
        )

    def list(self, username):
        raise NotImplementedError(
            f"{self.__class__.__name__}.list(username) Not Implemented."
        )

    def read(self, filename):
        raise NotImplementedError(
            f"{self.__class__.__name__}.read(filename) Not Implemented."
        )

    def dict2json(self, data_dict):
        data_json = json.dumps(data_dict, indent=self.json_indent)
        return data_json

    def json2dict(self, data_json):
        data_dict = json.loads(data_json)
        return data_dict


class S3(BaseStorage):
    def __init__(self):
        super().__init__()
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

    def write(self, filename, data):
        """Write data to file with filename in S3 Bucket"""
        json_data = self.dict2json(data)
        response = self._client.put_object(
            Bucket=self.bucket_name, Body=json_data, Key=filename
        )
        if not response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            logger.warning(response)
            return response

    def list(self, username=None):
        """List files with prefix username stored in S3"""
        response = self._client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=username
        )
        key_count = response["KeyCount"]
        try:
            contents = response["Contents"]
            keys = [file["Key"] for file in contents]
        except KeyError:
            logger.debug(response)
            keys = []
        return username, key_count, keys

    def read(self, filename):
        """Read file content of file with certain filename"""
        response = self._client.get_object(
            Bucket=self.bucket_name, Key=filename
        )
        data = response["Body"].read()
        return self.json2dict(data)


class LocalFileSystem(BaseStorage):
    def __init__(self):
        super().__init__()
        self.data_dir = settings.LOCAL_STORAGE_DIR

    def write(self, filename, data):
        """Write data to filename in local data_dir"""
        try:
            with open(self.data_dir / filename, "w") as f:
                json.dump(data, f, indent=self.json_indent)
        except FileNotFoundError:
            # Create subdir in data dir
            subdirs = filename.rsplit("/", 1)[0]
            new_dir = self.data_dir / subdirs
            new_dir.mkdir(exist_ok=True)
            with open(self.data_dir / filename, "w") as f:
                json.dump(data, f, indent=self.json_indent)

    def list(self, username=None):
        """List files in local data_dir"""
        username = username or ""
        files = []
        for file_ in self.data_dir.glob(f"*{username}*/*"):
            if file_.is_file():
                file_ = str(file_).split("/", 2)[-1]
                files.append(file_)
        return username, len(files), files

    def read(self, filename):
        """Read content in filename from local data_dir"""
        with open(self.data_dir / filename) as f:
            data = json.load(f)
        return data
