#!/usr/bin/env python
from abc import ABCMeta, abstractmethod
from typing import Dict
import logging
from ..cloudformation.elements import CloudFormationResource

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class ResourceProcessor(metaclass=ABCMeta):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._template_params = None

    @property
    @abstractmethod
    def tag(self):
        pass

    @abstractmethod
    def process(self, node: CloudFormationResource, params: Dict[str, dict]) -> Dict[str, dict]:
        pass
