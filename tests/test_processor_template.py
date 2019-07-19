#!/usr/bin/env python

from typing import Dict

from cfmacro.cloudformation.elements import CloudFormationResource
from cfmacro.core.base import ResourceProcessor
from cfmacro.core.engine import ProcessorEngine
from cfmacro.core.template import TemplateProcessor

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


def test_process(mocker, cloudformation_fragment, cloudformation_parameters):
    mocker.patch('cfmacro.core.template.TemplateProcessor.process_resources')
    tp = TemplateProcessor(ProcessorEngine())
    tp.process(fragment=cloudformation_fragment, template_params=cloudformation_parameters)
    tp.process_resources.assert_called_once_with(cloudformation_fragment['Resources'])


def test_process_resources(mocker, cloudformation_fragment, cloudformation_parameters):
    mocker.patch('cfmacro.core.template.TemplateProcessor.process_resource')

    class TestProcessor(ResourceProcessor):
        tag = 'TestTag'

        def process(self, node: CloudFormationResource, params: Dict[str, dict]):
            pass

    pe = ProcessorEngine()
    pe.register_processor(TestProcessor)
    tp = TemplateProcessor(pe)
    tp.process(fragment=cloudformation_fragment, template_params=cloudformation_parameters)
    tp.process_resource.assert_called()

