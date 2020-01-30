#!/usr/bin/env python
import hashlib
import os
from dataclasses import dataclass
from typing import Text

from boto3.session import Session
from mypy_boto3_s3 import S3Client

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


@dataclass
class S3Location:
    bucket: str
    key: str


class TemplateCache(object):
    def __init__(self):
        self._cache = {}
        self._session = Session()

    @staticmethod
    def _generate_cache_id(s3_location: S3Location):
        tmp = os.path.join(s3_location.bucket, s3_location.key)
        return hashlib.sha256(tmp.encode()).hexdigest()

    def get_template_data(self, template_location: S3Location) -> Text:
        cache_id = self._generate_cache_id(template_location)
        if self._cache.get(cache_id, None):
            return self._cache[cache_id]

        client: S3Client = self._session.client('s3')
        response = client.get_object(Bucket=template_location.bucket, Key=template_location.key)
        with response['Body'] as streaming_body:
            template_text = streaming_body.read()

        return template_text
