import json

import pytest

from cfmacro.cloudformation.elements import CloudFormationResource

CF_NODE_FIXTURE = '''
{
  "Type": "AWS::Bucket",
  "Properties": {
    "BucketName": { "Ref": "ParameterBucketName" },
    "NoReplaceNeeded": "true",
    "NoReplaceNeeded2": { "Key": "thisIsAKey", "Value": "thisIsAValue" },
    "InnerProperty": { "Fn::Sub": [ "${data}", { "data": { "Ref": "ParameterData" } } ] },
    "InsideList": [
      { "Element": { "Ref": "ParameterElement" } },
      { "Element2": "Value2" },
      { "Ref": "ParameterEntry3" }
    ]
  }
}
'''


@pytest.fixture(scope='module')
def cloudformation_resource():
    return CloudFormationResource('TestResource', json.loads(CF_NODE_FIXTURE))


@pytest.mark.parametrize('parameters, leaf, expected', [
    (
        {'ParameterBucketName': 'ValueParameterBucketName'},
        lambda x: x['Properties']['BucketName'],
        'ValueParameterBucketName'
    ),
    (
        {'ParameterBucketName': 'ValueParameterBucketName'},
        lambda x: x['Properties']['BucketName'],
        'ValueParameterBucketName'
    ),

])
def test_update_refs_from_dict(cloudformation_resource: CloudFormationResource, parameters, leaf, expected):
    cloudformation_resource.update_refs_from_dict(parameters)
    assert leaf(cloudformation_resource.node) == expected


CF_PARAMETERS = {
    'ParameterBucketName': 'ValueParameterBucketName',
    'ParameterData': 'ValueParameterData',
    'ParameterElement': 'ValueParameterElement',
    'ParameterEntry3': 'ValueParameterEntry3'
}

CF_NODE_REPLACED = '''
{
  "Type": "AWS::Bucket",
  "Properties": {
    "BucketName": "ValueParameterBucketName",
    "NoReplaceNeeded": "true",
    "NoReplaceNeeded2": { "Key": "thisIsAKey", "Value": "thisIsAValue" },
    "InnerProperty": { "Fn::Sub": [ "${data}", { "data": "ValueParameterData" } ] },
    "InsideList": [
      { "Element": "ValueParameterElement" },
      { "Element2": "Value2" },
      "ValueParameterEntry3"
    ]
  }
}
'''


def test_update_refs_from_dict_complete(cloudformation_resource: CloudFormationResource):
    global CF_PARAMETERS, CF_NODE_REPLACED
    cloudformation_resource.update_refs_from_dict(CF_PARAMETERS)
    assert cloudformation_resource.node == json.loads(CF_NODE_REPLACED)

