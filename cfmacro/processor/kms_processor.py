#!/usr/bin/env python
import logging
from typing import Dict, Union

from .base import ResourceProcessor
from ..cloudformation.elements import CloudFormationResource

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"



TEMPLATE = '''
"KMSKeyforRoleBusinessVpn": {
      "Type": "AWS::KMS::Key",
      "Properties": {
        "Description": "Key used from specific role",
        "KeyPolicy": {
          "Version": "2012-10-17",
          "Id": "KEY-POLICY",
          "Statement": [
            {
              "Sid": "Allow administration of the key",
              "Effect": "Allow",
              "Principal": {
                "AWS": [
                  { "Fn::Sub": [ "arn:aws:sts::${account}:root", { "account": { "Ref": "AWS::AccountId" } } ] }
                ]
              },
              "Action": [
                "kms:Create*",
                "kms:Describe*",
                "kms:Enable*",
                "kms:List*",
                "kms:Put*",
                "kms:Update*",
                "kms:Revoke*",
                "kms:Disable*",
                "kms:Get*",
                "kms:Delete*",
                "kms:ScheduleKeyDeletion",
                "kms:CancelKeyDeletion",
                "kms:TagResource"
              ],
              "Resource": "*"
            },
            {
              "Sid": "Allow use of the key for consuming",
              "Effect": "Allow",
              "Principal": {
                "AWS": [ 
                    {% for role_arn in role_capability_consuming %}
                        role_arn
                    {% endfor %}
                ]
              },
              "Action": [
                "kms:Decrypt",
                "kms:DescribeKey"
              ],
              "Resource": "*"
            },
            {
              "Sid": "Allow use of the key",
              "Effect": "Allow",
              "Principal": {
                "AWS": { "Fn::Sub": [ "arn:aws:iam::${account}:role/RoleCredentialServerCryptDecrypt", { "account": { "Ref": "AWS::AccountId" } } ] }
              },
              "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
              ],
              "Resource": "*"
            },
            {
              "Sid": "Allow use of the key",
              "Effect": "Allow",
              "Principal": {
                "AWS": { "Fn::Sub": [ "arn:aws:iam::${account}:role/RoleCredentialServerCryptOnly", { "account": { "Ref": "AWS::AccountId" } } ] }
              },
              "Action": [
                "kms:Encrypt",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
              ],
              "Resource": "*"
            }
          ]
        }
      }
    },
    "AliasKMSKeyforRoleBusinessVpn": {
      "Type": "AWS::KMS::Alias",
      "Properties": {
        "AliasName": "alias/RoleBusinessVpn",
        "TargetKeyId": {
          "Ref": "KMSKeyforRoleBusinessVpn"
        }
      }
    },
'''


class KMSProcessor(ResourceProcessor):
    tag = 'Custom::CfSnippetKMS'
    template = TEMPLATE


    def _generate_jinja_vars(self, properties):
        j2_vars = {}
        if not properties.get('RoleCapabilityUse', None):
            raise ValueError('Missing required property RoleCapabilityUse')
        pass
        # "RoleCapabilityConsuming": [""],
        # "RoleCapabilityEncrypt": [""],
        # "RoleCapabilityEncryptDecrypt": [""]

    def process(self, resource: CloudFormationResource, params: dict) -> Dict[str, dict]:
        self._template_params = params
        rules = self._parse_rules(resource.node)

        # if there are not rules we return back the node unparsed
        if not rules:
            return {resource.name: resource.node}

        result = {}
        for rule_id, rule in enumerate(rules):
            sg = self.sg_builder(resource.properties['Direction'],
                                 resource.properties['TargetGroup'],
                                 resource.properties['FromTo'],
                                 rule, rule_id)
            result[sg.name] = sg.node
        return result


class SgProcessor(ResourceProcessor):
    """
    Security Group Macro Processor
    """
    tag = 'Custom::CfSnippetSg'

    def __init__(self):
        """
        This processor support cloudformation elements like the following::

            "SgTestEgressRules": {
              "Type": "Custom::CfSnippetSg",
              "Properties": {
                "ServiceToken": "",
                "Direction": "Egress",
                "Rules": { "Ref": "WhitelistTest" },
                "FromTo": "Rabobank",
                "TargetGroup": {
                  "Ref": "SgTest"
                }
              }
            }

        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._template_params = None

    @staticmethod
    def target_group_to_name(tg):
        """ calculate the name from a target group node """
        if isinstance(tg, dict):
            name = tg.get('Ref', None)
        elif isinstance(tg, str):
            name = tg
        else:
            name = None
        if not name:
            raise ValueError('Unable to calculate Sg key name')
        return name

    @staticmethod
    def sg_builder(direction: str, target_group: Union[str, dict], label_from_to: str,
                   rule: dict, rule_number: int) -> CloudFormationResource:
        if direction.lower() == 'ingress':
            description = f'From {label_from_to}'
        else:
            description = f'To {label_from_to}'

        resource_name = SgProcessor.target_group_to_name(target_group).title()

        sg_key = (f"{resource_name}From{label_from_to}"
                  f"Proto{rule['proto'].upper()}Port{rule['from_port']}To{rule['to_port']}"
                  f"Ip{rule_number}")
        sg_value = {
            'Type': f'AWS::EC2::SecurityGroup{direction.title()}',
            'Properties': {
                'GroupId': target_group,
                'Description': description,
                'FromPort': rule['from_port'],
                'ToPort': rule['to_port'],
                'CidrIp': rule['cidr'],
                'IpProtocol': rule['proto'].lower()
            }
        }
        return CloudFormationResource(sg_key, sg_value)

    def _parse_rules(self, node: dict) -> list:
        rules_node = node['Properties']['Rules']

        # verify whether the node is a string or a ref to a parameter
        if isinstance(rules_node, dict) and rules_node.get('Ref', None):
            # it's a ref then we lookup the info from the parameters
            rules_data = self._template_params.get(rules_node['Ref'], None)
        elif isinstance(rules_node, str):
            rules_data = rules_node
        else:
            raise ValueError(f'Not a valid value for Rules: {rules_node}')

        # if the data is a plan string we split it as comma separated
        if isinstance(rules_data, str):
            rules = [elem.strip() for elem in rules_data.split(',')]
        elif isinstance(rules_data, list):
            rules = rules_data
        else:
            raise ValueError(f'Unsupported data in rules. Data: {rules_data}')

        processed_rules = []
        # for each rule entry we parse it as per format
        # proto:cidr:from-to
        for rule in rules:
            proto, cidr, port_range = rule.strip().split(':')
            if '-' in port_range:
                from_port, to_port = port_range.split('-')
            else:
                from_port = to_port = port_range
            processed_rules.append(dict(proto=proto.lower(),
                                        cidr=cidr,
                                        from_port=from_port,
                                        to_port=to_port))
        return processed_rules

    def process(self, resource: CloudFormationResource, params: dict) -> Dict[str, dict]:
        self._template_params = params
        rules = self._parse_rules(resource.node)

        # if there are not rules we return back the node unparsed
        if not rules:
            return {resource.name: resource.node}

        result = {}
        for rule_id, rule in enumerate(rules):
            sg = self.sg_builder(resource.properties['Direction'],
                                 resource.properties['TargetGroup'],
                                 resource.properties['FromTo'],
                                 rule, rule_id)
            result[sg.name] = sg.node
        return result
