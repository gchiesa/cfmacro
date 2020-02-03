import json
from pathlib import Path
import pytest
import boto3
from behave import *
from moto import mock_s3
from mypy_boto3_s3 import S3Client

from cfmacro.cloudformation.elements import CloudFormationTemplate
from cfmacro.core.engine import ProcessorEngine
from cfmacro.core.template import TemplateProcessor
from cfmacro.processors.inline_stack_processor import InlineStack
use_step_matcher("re")


def file_to_cf_template(filename: Path) -> CloudFormationTemplate:
    return CloudFormationTemplate(filename.read_text())


def dict_equals(dict_a, dict_b):
    j_a = json.dumps(dict_a, sort_keys=True, indent=2)
    j_b = json.dumps(dict_b, sort_keys=True, indent=2)
    return j_a == j_b


@given("a local template loaded from fixture (?P<input>.+)")
def step_impl(context, input):
    """
    :type context: behave.runner.Context
    :type input: str
    """
    context.cf_template_initial = file_to_cf_template(Path(context.fixture_path, input))


@step("a template loaded from fixture (?P<module>.+) is present on s3 with the key (?P<key>.+)")
def step_impl(context, module, key):
    """
    :type context: behave.runner.Context
    :type module: str
    :type key: str
    """
    context.cf_template_remote = file_to_cf_template(Path(context.fixture_path, module))
    c: S3Client = context.s3_client
    c.put_object(Bucket=context.s3_bucket, Key=key)


@then("the outcome template match the template loaded from the fixture (?P<outcome>.+)")
def step_impl(context, outcome):
    """
    :type context: behave.runner.Context
    :type outcome: str
    """
    processor_engine = ProcessorEngine()
    processor_engine.register_processor(InlineStack)
    template_processor = TemplateProcessor(processor_engine)
    template = context.cf_template_initial  # type: CloudFormationTemplate
    result = template_processor.process(fragment=template.template,
                                        template_params=template.parameters).to_dict()
    expected = file_to_cf_template(Path(context.fixture_path, outcome))

    assert dict_equals(result, expected.template)

