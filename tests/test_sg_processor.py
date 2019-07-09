#!/usr/bin/env python
import logging
import pytest
from cfmacro.processor import SgProcessor
from cfmacro.cloudformation.elements import CloudFormationResource

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


@pytest.mark.parametrize('target_group, expected_output', [
    ({'Ref': 'TestTargetGroup'}, 'TestTargetGroup'),
    ('TestTargetGroupString', 'TestTargetGroupString'),
    ({'Fn::GetAtt': ['TestTargetGroup', 'GroupId']}, 'TestTargetGroup')
])
def test_target_group_to_name(target_group, expected_output):
    assert SgProcessor.target_group_to_name(target_group) == expected_output


@pytest.mark.parametrize('bad_input', [
    (['TargetGroupName']),
    None,
    ({'Key': 'Value'}),
    ({'Fn::GetAttr': ['TestTargetGroup', 'VpcId']}, 'TestTargetGroup')
])
def test_target_group_to_name_wrong_input(bad_input):
    with pytest.raises(ValueError) as excinfo:
        SgProcessor.target_group_to_name(bad_input)
    assert 'Unable to calculate Sg key name' in str(excinfo.value)


@pytest.mark.parametrize('args, outcome', [
    (dict(direction='ingress', target_group='TargetGroupString', label_from_to='TestLabel',
          rule=dict(proto='tcp', cidr='192.168.0.1/16', from_port='80', to_port='80'),
          rule_number=0),
     CloudFormationResource('TargetgroupstringFromTestLabelProtoTCPPort80To80Ip0', {
         'Type': 'AWS::EC2::SecurityGroupIngress',
         'Properties': {
             'GroupId': 'TargetGroupString',
             'Description': 'From TestLabel',
             'FromPort': '80',
             'ToPort': '80',
             'CidrIp': '192.168.0.1/16',
             'IpProtocol': 'tcp'
         }
     }))
])
def test_sg_builder(args: dict, outcome: CloudFormationResource):
    r = SgProcessor.sg_builder(**args)
    assert r.name == outcome.name
    assert r.node == outcome.node


@pytest.mark.parametrize('rules, ruleset, params', [
    # test : rules as string with single entry
    ('tcp:192.168.0.1/24:80',
     [dict(proto='tcp',
           cidr='192.168.0.1/24',
           from_port='80',
           to_port='80')],
     {}),
    # test : rules as string with multiple comma separated entries
    ('tcp:192.168.1.1/32:80, tcp:192.168.1.2/32:80, udp:10.10.10.10/32:20-21',
     [dict(proto='tcp',
           cidr='192.168.1.1/32',
           from_port='80',
           to_port='80'),
      dict(proto='tcp',
           cidr='192.168.1.2/32',
           from_port='80',
           to_port='80'),
      dict(proto='udp',
           cidr='10.10.10.10/32',
           from_port='20',
           to_port='21')
      ],
     {}),
    # test : rules in parameters as list of strings
    ({'Ref': 'testRules'},
     [dict(proto='tcp',
           cidr='192.168.1.1/32',
           from_port='80',
           to_port='80'),
      dict(proto='tcp',
           cidr='192.168.1.2/32',
           from_port='80',
           to_port='80'),
      dict(proto='udp',
           cidr='10.10.10.10/32',
           from_port='20',
           to_port='21')
      ],
     {'testRules': ['tcp:192.168.1.1/32:80', 'tcp:192.168.1.2/32:80', 'udp:10.10.10.10/32:20-21']})
])
def test_parse_rules(rules, ruleset, params):
    node = {
        'Properties': {
            'Rules': rules
        }
    }

    sgp = SgProcessor()
    sgp._template_params = params
    processed_rules = sgp._parse_rules(node)
    assert processed_rules == ruleset
