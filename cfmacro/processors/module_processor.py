#!/usr/bin/env python
import json
import logging
from ..cloudformation.elements import CloudFormationResource
from typing import Dict, List, Text
from ..core.base import ResourceProcessor

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class CloudFormationTemplateException(Exception):
    pass


class CloudFormationTemplate(object):
    def __init__(self, text: Text):
        self._raw = text
        self.template = {}
        self.parameters = {}
        self.resources = []
        self.parse()

    def parse(self):
        try:
            self.template = json.loads(self._raw)
        except ValueError as e:
            raise CloudFormationTemplateException(f'Invalid template. Error: {e}')

        self.parameters = self.template.get('Parameters', {})
        for res_name, res_node in self.template.get('Resources', {}).items():
            self.resources.append(CloudFormationResource(res_name, res_node))

    def update_refs_from_dict(self, parameters: Dict):
        for resource in self.resources:  # type: CloudFormationResource
            resource.update_refs_from_dict(parameters)


class IncludeModuleException(Exception):
    pass


class ModuleProcessor(ResourceProcessor):
    tag = 'Custom::ModuleProcessorV1'

    def __init__(self, template: CloudFormationTemplate):
        self._cf = template
        self.custom_parameters = {}

    def with_parameters(self, parameters: Dict):
        self.custom_parameters = parameters

    def _prepare_parameters(self) -> Dict:
        """
        build the final parameters dict using the custom parameters and the defaults from the template.
        If some default is missing it will raise exception

        :return: dict of parameters
        """
        result = {}
        for param_name, param_node in self._cf.parameters.items():
            result[param_name] = param_node.get('Default', None)
            if param_name in self.custom_parameters.keys():
                result[param_name] = self.custom_parameters[param_name]
            if result[param_name] is None:
                raise IncludeModuleException(f'Missing default of parameter for {param_name}')
        return result

    def render_include(self):
        parameters = self._prepare_parameters()
        self._cf.update_refs_from_dict(parameters)

    def process(self, node: CloudFormationResource, params: Dict[str, dict]) -> Dict[str, dict]:
        pass

