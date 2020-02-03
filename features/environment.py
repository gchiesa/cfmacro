import os

import boto3
from moto import mock_s3
from mypy_boto3_s3 import S3Client

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
S3_BUCKET = '123456789012'


def before_all(context):
    context.fixture_path = FIXTURE_PATH
    mock = mock_s3()
    mock.start()
    context.mock_s3 = mock


def after_all(context):
    context.mock_s3.stop()


def before_feature(context, feature):
    c: S3Client = boto3.client('s3')
    context.s3_bucket = S3_BUCKET
    context.s3_client = c
    c.create_bucket(Bucket=S3_BUCKET)


def after_feature(context, feature):
   c: S3Client = context.s3_client
   c.delete_bucket(Bucket=context.s3_bucket)
