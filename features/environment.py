import os

import boto3
from moto import mock_s3, mock_sts
from mypy_boto3_s3 import S3Client
from mypy_boto3_sts import STSClient

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
S3_BUCKET = '123456789012'


def before_all(context):
    os.environ['AWS_REGION'] = 'eu-west-1'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'
    context.fixture_path = FIXTURE_PATH
    context.mock_s3 = mock_s3()
    context.mock_s3.start()
    context.mock_sts = mock_sts()
    context.mock_sts.start()


def after_all(context):
    context.mock_s3.stop()


def before_feature(context, feature):
    c: S3Client = boto3.client('s3')
    context.s3_bucket = S3_BUCKET
    context.s3_client = c
    c.create_bucket(Bucket=S3_BUCKET)


def after_feature(context, feature):
    c: S3Client = context.s3_client
    c.delete_objects(Bucket=context.s3_bucket)
    c.delete_bucket(Bucket=context.s3_bucket)
