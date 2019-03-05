#!/usr/bin/env python
import json
import logging

import pytest

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


CF_FRAGMENT_FIXTURE = '''
{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "test for security group",
  "Parameters": {
    "WhitelistTest": {
      "Type": "List<String>",
      "Description": "List of CIDRS to whitelist",
      "Default": "tcp:10.0.0.1/32:80, udp:10.10.10.0/24:53, tcp:10.10.10.0/24:21-22"
    }
  },
  "Transform": [
    "CfSnippetSg"
  ],
  "Resources": {
    "SgTest": {
      "Type": "AWS::EC2::SecurityGroup",
      "Properties": {
        "GroupName": "SgTest",
        "GroupDescription": "Security Group Test"
      }
    },
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
  }
}
'''

CF_PARAMETERS_FIXTURE = {
    'WhitelistTest': ["tcp:10.0.0.1/32:80", "udp:10.10.10.0/24:53", "tcp:10.10.10.0/24:21-22"]
}


@pytest.fixture()
def cloudformation_fragment():
    return json.loads(CF_FRAGMENT_FIXTURE)


@pytest.fixture()
def cloudformation_parameters():
    return CF_PARAMETERS_FIXTURE
