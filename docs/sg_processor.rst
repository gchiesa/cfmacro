SgProcessor
===========

This processor extend the AWS Cloud Formation DSL by adding a powerful Security Group Rules generator.

Overview
--------
With this resource type you will be able to abstract the customisation of the Security Groups in your template/blueprint
and ingest the rules via parameters. In this way you can create highly reusable templates for your Infrastructure As
Code.


The resource type declaration looks like the following:

.. code-block:: json

    "SgTestEgressRules": {
      "Type": "Custom::CfSnippetSg",
      "Properties": {
        "ServiceToken": "",
        "Direction": "Ingress",
        "Rules": { "Ref": "WhitelistMyIps" },
        "FromTo": "WhitelistMyIps",
        "TargetGroup": { "Fn::GetAtt": [ "SgTest", "GroupId" ] }
      }
    }

And int the template you can then parametrise the list of IPs and ports to open like the following:

.. code-block:: json

  "Parameters": {
    "WhitelistMyIps": {
      "Type": "List<String>",
      "Description": "List of CIDRS to whitelist",
      "Default": "tcp:10.0.0.1/32:80, udp:10.10.10.0/24:53, tcp:10.10.10.0/24:21-22"
    }
  }

Check the example_template_ for the complete Cloud Formation template

Usage
-----

The DSL of the newly available resource supports the following properties:

- **ServiceToken** (required): it's ignored but only required to make the resource conform to the AWS Custom Resources in
  Cloud Formation

- **Direction** (required): represent the type of security group rules you want to implement.

  - Allowed values: ``Ingress, Egress``

- **Rules** (required): the set of rules that you want to create. It supports various formats.
  See the `Rules`_ section

- **FromTo** (optional): a label that represent the Destination/Source security group (depending on the
  direction. It's used also to compose the resource name and the Description

- **TargetGroup** (required): the SecurityGroupId on which the generated SecurityGroupIngress/Egress will be attached.
  It supports multiple type of values/declarations. See `Target Group`_ section for more information.

- **TargetGroupLabel** (optional): The label to use instead trying to derive the label from the TargetGroup property.

Rules
-----

The rule is the core element that holds the information for the Security Group Ingress / Egress creation.

The DSL resource SgProcessor will be converted in a number of Security Group Ingress/Egress depending how many rules you
specify in this section.

A rule it's a simple plain string in the form::

    <protocol>:<cidr_or_resource>:<port_range>

Multiple rules compose a ruleset. A ruleset can be expressed in:

- a comma separated list of rules::

    <rule>, <rule>, ... , <rule>

- a list of rules::

    [ <rule>, <rule>, ... , <rule> ]

Rule Fields
-----------

- **<protocol>** (required): the procotol for which the rule apply.

  - Allowed values: ``tcp, udp, icmp``

- **<cidr_or_resource>** (required): this can be a valid Cidr or a string that the processor will use implement the
  Source/DestinationGroupId.

  - if the value is a valid **Cidr** then the output will be a Cidr also in the security group.

    Example:

    ``tcp:192.168.1.0/24:80`` => ``"Cidr": "192.168.1.0/24"``

  - if the value has the form **Resource.Attribute** then the output will be a Fn::GetAtt to that resource and the
    attribute the specified attribute name after the dot.

    Example:

    ``tcp:SgTest.GroupId:80`` => ``"DestinationGroupId": { "Fn::GetAtt": [ "SgTest", "GroupId" ] }``

  - if the value has the form **Parameters/SomeParameter** then the output will be resolved by looking to the template
    parameters and taking the value from the related entry.

    Example:

    ``tcp:Parameters/SgTest:80`` => ``"SourceGroupId": "sg-12345678"``

  - if the value has the form **Import/SomeImport** then the output will be rendered as Fn::ImportValue with the related
    import name.

    Example:

    ``tcp:Imports/SgTest:80`` => ``"DestinationGroupId": { "Fn::ImportValue": "SgTest" }``

- **<port_range>** (required): a single port or a port range (Eg. 20-21) or special value ``ALL``

Target Group
------------

Target group defines the Security Group on which connect the generated rule.




.. _example_template: https://github.com/gchiesa/cfmacro/blob/master/cfmacro/_resources/examples/cf_snippet_sg.template
