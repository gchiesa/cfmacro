#!/usr/bin/env python
import copy
import json
from typing import Dict, Union

from .base import ResourceProcessor
from .engine import ProcessorEngine
from ..cloudformation.elements import CloudFormationResource

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class TemplateProcessor(object):
    def __init__(self, processor_engine: ProcessorEngine):
        self._processor_engine = processor_engine
        self._template = None
        self._processed_template = None
        self._processed_resources = None
        self._template_params = {}

    def process(self, fragment: Dict[str, dict], template_params: Dict[str, Union[dict, list, str]]):
        self._template = fragment
        self._template_params = template_params
        self._processed_resources = self.process_resources(self._template['Resources'])
        self._processed_template = copy.deepcopy(self._template)
        self._processed_template['Resources'] = self._processed_resources
        return self

    def process_resources(self, resources: Dict[str, dict]) -> Dict[str, dict]:
        processed_resources = {}
        for resource_name, resource_node in resources.items():
            resource = CloudFormationResource(resource_name, resource_node)
            for name, node in self.process_resource(resource).items():
                processed_resources[name] = node
        return processed_resources

    def process_resource(self, resource: CloudFormationResource) -> Dict[str, dict]:
        result = {
            resource.name: resource.node
        }
        if self._processor_engine.processor_map.get(resource.node['Type'], None):
            # instantiate the proper core for the node type
            processor = self._processor_engine.processor_map[resource.node['Type']]()  # type: ResourceProcessor
            # apply the core
            result = processor.process(resource, self._template_params)
        return result

    def to_dict(self):
        return self._processed_template

    def to_json(self):
        json_data = json.dumps(self._processed_template, indent=2)
        return json_data


__all__ = [
    TemplateProcessor
]
