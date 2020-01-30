#!/usr/bin/env python
from boto3.session import Session
from mypy_boto3_sts import STSClient

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class SingletonAWSVariables(object):
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class AWSVariables(SingletonAWSVariables):
    def __init__(self):
        SingletonAWSVariables.__init__(self)
        self._session = Session()
        sts: STSClient = self._session.client('sts')
        self._account_id = sts.get_caller_identity().get('Account')

    @property
    def region(self):
        return self._session.region_name

    @property
    def account_id(self):
        return self._account_id

    def __str__(self):
        return str(self._session)
