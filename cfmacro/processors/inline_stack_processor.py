#!/usr/bin/env python
import logging
from collections.abc import Iterable
from typing import Dict

from boto3.session import Session

from .inline_stack.include_module import IncludeModule
from .inline_stack.template_cache import TemplateCache, S3Location
from ..cloudformation.elements import CloudFormationResource, CloudFormationTemplate
from ..core.base import ResourceProcessor
from ..utils.aws_variables import AWSVariables

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class InlineStackException(Exception):
    pass


class InlineStack(ResourceProcessor):
    tag = 'Custom::InlineStackV1'

    def __init__(self, template_cache_provider=None):
        """
        DSL that allow the inclusion of a stack inline instead of inner
        Example:

        {
          "Type": "Custom::InlineStackV1",
          "Properties": {
            "ResourcePrefix": "PrefixToPrependToEachResource",
            "TemplateUri": "TemplatePathOnS3 - example s3://bucket/uri/name",
            "TemplateParameters": [
              {
                "Parameter1": "Value1"
              },
              {
                "Parameter1": "Value2ForSecondIteration"
              }
            ]
          }
        }

        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._cache = template_cache_provider or TemplateCache()
        self._node = None
        self._template_location = None
        self._template_parameters = None
        self._session = Session

    def _validate_properties(self):
        """
        Validate if all the information required are present
        :return:
        """
        properties = self._node.get('Properties', {})

        template_uri = properties.get('TemplateUri', None)
        if template_uri is None or not template_uri:
            raise InlineStackException('Property TemplateUri not provided')
        self._template_location = self._parse_template_uri(template_uri)

        self._resource_prefix = properties.get('ResourcePrefix', None)
        if self._resource_prefix is None:
            raise InlineStackException('Property ResourcePrefix not provided')

        parameters = properties.get('TemplateParameters', None)
        if parameters is None or not isinstance(parameters, Iterable):
            raise InlineStackException('Property TemplateParameters not provided or not correct')
        self._template_parameters = self._parse_template_parameters(parameters)

    def process(self, node: CloudFormationResource, params: Dict[str, dict]) -> Dict[str, dict]:
        """

        :param node: The node that represent the macro resource
        :param params: The main template parameters
        :return: one or more resources
        """
        self._node = node
        self._validate_properties()
        try:
            template_data = self._cache.get_template_data(self._template_location)
        except Exception as e:
            raise InlineStackException(f'Error while retrieving remote template to include. Type:{str(type(e))}. '
                                       f'Error: {str(e)}')

        self.logger.debug(f'Retrieved template data: {template_data}')

        # allocate the include module object
        include_module = IncludeModule(CloudFormationTemplate(template_data))
        generated_resources = include_module.with_parameters(params).generate_resources()
        result = {}
        for resource in generated_resources:
            result[resource.name] = resource.node
        self.logger.debug(f'Result: {result}')
        return result

    @staticmethod
    def _parse_template_uri(template_uri: str) -> S3Location:
        """
        Template uri should start https:// or s3://
        and can contain AWS variables like
            AWS::AccountId
            AWS::Region
        :param template_uri:
        :return:
        """
        aws_variables = AWSVariables()
        result = (template_uri
                  .replace('${AWS::AccountId}', aws_variables.account_id)
                  .replace('${AWS::Region', aws_variables.region))
        if result.startswith('https://'):
            result = result[8:]
        elif result.startswith('s3://'):
            result = result[5:]
        bucket, _, key = result.partition('/')
        return S3Location(bucket, key)

    @staticmethod
    def _parse_template_parameters(parameters: Iterable) -> Iterable:
        if isinstance(parameters, dict):
            return [parameters]
        return parameters


