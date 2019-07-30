# Created by gchiesa at 2019-07-21
Feature: Security Group Processor Integration Tests
  # Enter feature description here

  Scenario: Template with basic usage of security group processor
    Given a sample cloudformation template containing security group macro
        """
        {
          "AWSTemplateFormatVersion": "2010-09-09",
          "Description": "test for security group",
          },
          "Transform": [
            "CFProcessor"
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
              "Type": "Custom::SgProcessorV1",
              "Properties": {
                "ServiceToken": "",
                "Direction": "Ingress",
                "Rules": [
                    "tcp:192.168.78.0/24:443",
                    "tcp:192.168.79.10/32:22"
                ],
                "FromTo": "Whitelist Office",
                "TargetGroup": { "Fn::GetAtt": [ "SgTest", "GroupId" ] }
              }
            }
          }
        }
        """
    When we run the security group macro processor
    Then the resulting cloudformation template is the following
        """
        {
          "AWSTemplateFormatVersion": "2010-09-09",
          "Description": "test for security group",
          },
          "Transform": [
            "CFProcessor"
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
              "Type": "Custom::SgProcessorV1",
              "Properties": {
                "ServiceToken": "",
                "Direction": "Ingress",
                "Rules": [
                    "tcp:192.168.78.0/24:443",
                    "tcp:192.168.79.10/32:22"
                ],
                "FromTo": "Whitelist Office",
                "TargetGroup": { "Fn::GetAtt": [ "SgTest", "GroupId" ] }
              }
            }
          }
        }
        """

