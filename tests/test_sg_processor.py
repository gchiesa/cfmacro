#!/usr/bin/env python
import pytest

from cfmacro.cloudformation.elements import CloudFormationResource
from cfmacro.processors import SgProcessor
from cfmacro.processors.sg_processor import Rule

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('target_group_id, target_group_label, expected_output', [
    (
            {'Ref': 'TestTargetGroup'},
            '',
            'TestTargetGroup'
    ),
    (
            'TestTargetGroupString',
            '',
            'TestTargetGroupString'
    ),
    (
            {'Fn::GetAtt': ['TestTargetGroup', 'GroupId']},
            '',
            'TestTargetGroup'
    ),
    (
            {'Fn::ImportValue': {'Fn::Sub': '${Test}-TargetGroupId'}},
            'TargetGroupFromLabel',
            'TargetGroupFromLabel'
    ),
])
def test_target_group_to_name(target_group_id, target_group_label, expected_output):
    assert SgProcessor.target_group_to_name(target_group_id, target_group_label) == expected_output


# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('bad_input', [
    (
            ['TargetGroupName']
    ),
    None,
    (
            {'Key': 'Value'}
    ),
    (
            {'Fn::GetAttr': ['TestTargetGroup', 'VpcId']},
            'TestTargetGroup'
    )
])
def test_target_group_to_name_wrong_input(bad_input):
    with pytest.raises(ValueError) as excinfo:
        SgProcessor.target_group_to_name(bad_input)
    assert 'Unable to calculate Sg key name' in str(excinfo.value)


# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('target_group_id, target_group_label', [
    (
            {'Fn::ImportValue': {'Fn::Sub': '${Test}-TargetGroupId'}},
            None,
    ),
])
def test_target_group_to_name_target_group_label_required(target_group_id, target_group_label):
    with pytest.raises(ValueError) as excinfo:
        SgProcessor.target_group_to_name(target_group_id, target_group_label)
    assert 'TargetGroupLabel is required' in str(excinfo.value)


# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('args, outcome', [
    # TEST: 0 - testing with simple cidr
    (
            dict(direction='ingress', target_group='TargetGroupString', label_from_to='TestLabel',
                 rule=Rule(proto='tcp', cidr_or_sg='192.168.0.0/16', from_port='80', to_port='80'),
                 rule_number=0),
            CloudFormationResource('TargetGroupStringFromTestLabelProtoTCPPort80To80Entry0', {
                'Type': 'AWS::EC2::SecurityGroupIngress',
                'Properties': {
                    'GroupId': 'TargetGroupString',
                    'Description': 'From TestLabel',
                    'FromPort': '80',
                    'ToPort': '80',
                    'CidrIp': '192.168.0.0/16',
                    'IpProtocol': 'tcp'
                }
            })
    ),
    # TEST: 1 - testing with Fn::GetAtt for cidr that should be converted in DestinationGroupId
    (
            dict(direction='egress', target_group='SgVPC', label_from_to='SgTestLabel',
                 rule=Rule(proto='tcp', cidr_or_sg='CustomResourceLambda.security_group_id',
                           from_port='80', to_port='80'),
                 rule_number=1),
            CloudFormationResource('SgVPCToSgTestLabelProtoTCPPort80To80Entry1', {
                'Type': 'AWS::EC2::SecurityGroupEgress',
                'Properties': {
                    'GroupId': 'SgVPC',
                    'Description': 'To SgTestLabel',
                    'FromPort': '80',
                    'ToPort': '80',
                    'DestinationSecurityGroupId': {'Fn::GetAtt': ["CustomResourceLambda", "security_group_id"]},
                    'IpProtocol': 'tcp'
                }
            })
    ),
    # TEST: 2 - testing when cidr is a security group (string) like sg-12345678
    (
            dict(direction='ingress', target_group='SgVPC', label_from_to='SgTestLabel',
                 rule=Rule(proto='tcp', cidr_or_sg='CustomResourceLambda.security_group_id',
                           from_port='80', to_port='80'),
                 rule_number=2),
            CloudFormationResource('SgVPCFromSgTestLabelProtoTCPPort80To80Entry2', {
                'Type': 'AWS::EC2::SecurityGroupIngress',
                'Properties': {
                    'GroupId': 'SgVPC',
                    'Description': 'From SgTestLabel',
                    'FromPort': '80',
                    'ToPort': '80',
                    'SourceSecurityGroupId': {'Fn::GetAtt': ["CustomResourceLambda", "security_group_id"]},
                    'IpProtocol': 'tcp'
                }
            })
    ),
    # TEST: 3 - testing when target group is a ref to another group
    (
            dict(direction='egress', target_group={'Ref': 'SgVPC'}, label_from_to='SgTestLabel',
                 rule=Rule(proto='tcp', cidr_or_sg='CustomResourceLambda.GroupId',
                           from_port='80', to_port='80'),
                 rule_number=3),
            CloudFormationResource('SgVPCToSgTestLabelProtoTCPPort80To80Entry3', {
                'Type': 'AWS::EC2::SecurityGroupEgress',
                'Properties': {
                    'GroupId': {'Ref': 'SgVPC'},
                    'Description': 'To SgTestLabel',
                    'FromPort': '80',
                    'ToPort': '80',
                    'DestinationSecurityGroupId': {'Fn::GetAtt': ["CustomResourceLambda", "GroupId"]},
                    'IpProtocol': 'tcp'
                }
            })
    ),
    # TEST: 4 - testing when label_from_to is empty then it's calculated based on the cidr_or_sg
    (
            dict(direction='egress', target_group={'Ref': 'SgVPC'}, label_from_to='',
                 rule=Rule(proto='tcp', cidr_or_sg='CustomResourceLambda.GroupId',
                           from_port='80', to_port='80', raw_rule='tcp:CustomResourceLambda.GroupId:80'),
                 rule_number=4),
            CloudFormationResource('SgVPCToCustomResourceLambdaProtoTCPPort80To80Entry4', {
                'Type': 'AWS::EC2::SecurityGroupEgress',
                'Properties': {
                    'GroupId': {'Ref': 'SgVPC'},
                    'Description': 'To CustomResourceLambda',
                    'FromPort': '80',
                    'ToPort': '80',
                    'DestinationSecurityGroupId': {'Fn::GetAtt': ["CustomResourceLambda", "GroupId"]},
                    'IpProtocol': 'tcp'
                }
            })
    ),
    # TEST: 5 - testing when label_from_to is empty then it's calculated based on the cidr_or_sg that refers to a
    # parameter
    (
            dict(direction='egress', target_group={'Ref': 'SgVPC'}, label_from_to='',
                 rule=Rule(proto='tcp', cidr_or_sg='sg-12345678',
                           from_port='80', to_port='80', raw_rule='tcp:Parameters/SgTest:80'),
                 rule_number=5),
            CloudFormationResource('SgVPCToSgTestProtoTCPPort80To80Entry5', {
                'Type': 'AWS::EC2::SecurityGroupEgress',
                'Properties': {
                    'GroupId': {'Ref': 'SgVPC'},
                    'Description': 'To SgTest',
                    'FromPort': '80',
                    'ToPort': '80',
                    'DestinationSecurityGroupId': 'sg-12345678',
                    'IpProtocol': 'tcp'
                }
            })
    ),
    # TEST: 6 - testing when a import with simple variable is in the rule
    (
            dict(direction='egress', target_group={'Ref': 'SgVPC'}, label_from_to='SgTest',
                 rule=Rule(proto='tcp', cidr_or_sg='Import/Admin-SgTest',
                           from_port='80', to_port='80', raw_rule='tcp:Import/Admin-SgTest:80'),
                 rule_number=6),
            CloudFormationResource('SgVPCToSgTestProtoTCPPort80To80Entry6', {
                'Type': 'AWS::EC2::SecurityGroupEgress',
                'Properties': {
                    'GroupId': {'Ref': 'SgVPC'},
                    'Description': 'To SgTest',
                    'FromPort': '80',
                    'ToPort': '80',
                    'DestinationSecurityGroupId': {'Fn::ImportValue': {'Fn::Sub': 'Admin-SgTest'}},
                    'IpProtocol': 'tcp'
                }
            })
    ),
    # TEST: 7 - testing when a import with expandable variable is in the rule
    (
            dict(direction='egress', target_group={'Ref': 'SgVPC'}, label_from_to='SgTest',
                 rule=Rule(proto='tcp', cidr_or_sg='Import/${StackName}-SgTest',
                           from_port='80', to_port='80', raw_rule='tcp:Import/${StackName}-SgTest:80'),
                 rule_number=7),
            CloudFormationResource('SgVPCToSgTestProtoTCPPort80To80Entry7', {
                'Type': 'AWS::EC2::SecurityGroupEgress',
                'Properties': {
                    'GroupId': {'Ref': 'SgVPC'},
                    'Description': 'To SgTest',
                    'FromPort': '80',
                    'ToPort': '80',
                    'DestinationSecurityGroupId': {'Fn::ImportValue': {'Fn::Sub': '${StackName}-SgTest'}},
                    'IpProtocol': 'tcp'
                }
            })
    ),
    # TEST: 8 - testing when target group is an import simple
    (
            dict(direction='ingress', target_group={'Fn::ImportValue': 'Admin-Target'}, label_from_to='TestSg',
                 label_target_group='TargetGroupLabel',
                 rule=Rule(proto='tcp', cidr_or_sg='192.168.0.0/16', from_port='80', to_port='80'),
                 rule_number=8),
            CloudFormationResource('TargetGroupLabelFromTestSgProtoTCPPort80To80Entry8', {
                'Type': 'AWS::EC2::SecurityGroupIngress',
                'Properties': {
                    'GroupId': {'Fn::ImportValue': 'Admin-Target'},
                    'Description': 'From TestSg',
                    'FromPort': '80',
                    'ToPort': '80',
                    'CidrIp': '192.168.0.0/16',
                    'IpProtocol': 'tcp'
                }
            })
    ),
    # TEST: 9 - testing when target group is an import simple
    (
            dict(direction='egress', target_group={'Ref': 'SgVPC'}, label_from_to='',
                 rule=Rule(proto='tcp', cidr_or_sg='Import/${StackName}-SgTest',
                           from_port='80', to_port='80', raw_rule='tcp:Import/${StackName}-SgTest:80'),
                 rule_number=9),
            CloudFormationResource('SgVPCToStackNameSgTestProtoTCPPort80To80Entry9', {
                'Type': 'AWS::EC2::SecurityGroupEgress',
                'Properties': {
                    'GroupId': {'Ref': 'SgVPC'},
                    'Description': 'To StackNameSgTest',
                    'FromPort': '80',
                    'ToPort': '80',
                    'DestinationSecurityGroupId': {'Fn::ImportValue': {'Fn::Sub': '${StackName}-SgTest'}},
                    'IpProtocol': 'tcp'
                }
            })
    ),
])
def test_sg_builder(args: dict, outcome: CloudFormationResource):
    processor = SgProcessor()
    resource = processor.sg_builder(**args)
    assert resource.name == outcome.name
    assert resource.node == outcome.node


# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize('rules, cloudformation_parameters, result_ruleset', [
    # test : rules as string with single entry
    (
            'tcp:192.168.0.0/24:80',
            {},
            [
                Rule(proto='tcp',
                     cidr_or_sg='192.168.0.0/24',
                     from_port='80',
                     to_port='80')
            ],
    ),
    # test : rules as string with single entry
    (
            'icmp:192.168.1.0/24:ALL',
            {},
            [
                Rule(proto='icmp',
                     cidr_or_sg='192.168.1.0/24',
                     from_port='-1',
                     to_port='-1')
            ]
    ),
    # test : rules as string with multiple comma separated entries
    (
            'tcp:192.168.1.1/32:80, tcp:192.168.1.2/32:80, udp:10.10.10.10/32:20-21',
            {},
            [
                Rule(proto='tcp',
                     cidr_or_sg='192.168.1.1/32',
                     from_port='80',
                     to_port='80'),
                Rule(proto='tcp',
                     cidr_or_sg='192.168.1.2/32',
                     from_port='80',
                     to_port='80'),
                Rule(proto='udp',
                     cidr_or_sg='10.10.10.10/32',
                     from_port='20',
                     to_port='21')

            ]
    ),
    # test : rules as list of strings
    (
            ['tcp:192.168.1.1/32:80', 'tcp:192.168.1.2/32:80', 'udp:10.10.10.10/32:20-21'],
            {},
            [
                Rule(proto='tcp',
                     cidr_or_sg='192.168.1.1/32',
                     from_port='80',
                     to_port='80'),
                Rule(proto='tcp',
                     cidr_or_sg='192.168.1.2/32',
                     from_port='80',
                     to_port='80'),
                Rule(proto='udp',
                     cidr_or_sg='10.10.10.10/32',
                     from_port='20',
                     to_port='21')
            ]
    ),
    # test : rules in parameters as list of strings
    (
            {'Ref': 'testRules'},
            {'testRules': ['tcp:192.168.1.1/32:80', 'tcp:192.168.1.2/32:80', 'udp:10.10.10.10/32:20-21']},
            [
                Rule(proto='tcp',
                     cidr_or_sg='192.168.1.1/32',
                     from_port='80',
                     to_port='80'),
                Rule(proto='tcp',
                     cidr_or_sg='192.168.1.2/32',
                     from_port='80',
                     to_port='80'),
                Rule(proto='udp',
                     cidr_or_sg='10.10.10.10/32',
                     from_port='20',
                     to_port='21')
            ]

    ),
    # test : rules as string with destinationGroupIds instead cidrs
    (
            'tcp:sg-12345678:80, tcp:SgTest.GroupId:80, udp:CustomResourceLambda.security_group_id:20-21',
            {},
            [
                Rule(proto='tcp',
                     cidr_or_sg='sg-12345678',
                     from_port='80',
                     to_port='80'),
                Rule(proto='tcp',
                     cidr_or_sg='SgTest.GroupId',
                     from_port='80',
                     to_port='80'),
                Rule(proto='udp',
                     cidr_or_sg='CustomResourceLambda.security_group_id',
                     from_port='20',
                     to_port='21')
            ]
    ),
    # test : rules as string with cidr_or_sg that refers to a parameter
    (
            'tcp:sg-12345678:80, tcp:Parameters/SgTest:80, udp:CustomResourceLambda.security_group_id:20-21',
            {'SgTest': 'sg-87654321'},
            [
                Rule(proto='tcp',
                     cidr_or_sg='sg-12345678',
                     from_port='80',
                     to_port='80'),
                Rule(proto='tcp',
                     cidr_or_sg='sg-87654321',
                     from_port='80',
                     to_port='80'),
                Rule(proto='udp',
                     cidr_or_sg='CustomResourceLambda.security_group_id',
                     from_port='20',
                     to_port='21')
            ]
    ),
    # test : rules as string with port range and custom resource to lookup
    (
            'tcp:CustomResourceLambda.security_group_id:1024-65535',
            {},
            [
                Rule(proto='tcp',
                     cidr_or_sg='CustomResourceLambda.security_group_id',
                     from_port='1024',
                     to_port='65535')
            ]
    ),
    # test : rules contains reference to import with simple variable name
    (
            'tcp:Imports/TestSgGroupId:80',
            {},
            [
                Rule(proto='tcp',
                     cidr_or_sg='Imports/TestSgGroupId',
                     from_port='80',
                     to_port='80')
            ]
    ),
    # test : rules contains reference to import with sub to expand variable name
    (
            'tcp:Imports/${StackName}-TestSgGroupId:80',
            {},
            [
                Rule(proto='tcp',
                     cidr_or_sg='Imports/${StackName}-TestSgGroupId',
                     from_port='80',
                     to_port='80')
            ]
    ),
])
def test_parse_rules(rules, cloudformation_parameters, result_ruleset):
    node = {
        'Properties': {
            'Rules': rules
        }
    }
    sgp = SgProcessor()
    sgp._template_params = cloudformation_parameters
    processed_rules = sgp._parse_rules(node)

    assert processed_rules == result_ruleset
