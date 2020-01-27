#!/usr/bin/env python

from typing import Dict, Union, List, AnyStr

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class CloudFormationResource(object):
    def __init__(self, name: str, node: dict):
        self.name = name
        self.node = node

    @property
    def properties(self):
        return self.node.get('Properties', None)

    def add_dependencies(self, dependencies=None):
        if dependencies:
            self.node['DependsOn'] = dependencies

    def update_refs_from_dict(self, parameters: Dict):
        """
        traverse the node and replace the refs that point to a key in the parameters with the relative value

        example, node:
        {
            "Type": "AWS::Bucket",
            "Properties": {
                "BucketName": { "Ref": "CustomBucketName" },
                "NoReplaceNeeded": "true",
                "NoReplaceNeeded2": { "Key": "thisIsAKey", "Value": "thisIsAValue" },
                "InnerProperty": { "Fn::Sub": [ "${data}", { "data" : { "Ref": "CustomData" } } ] }
                "InsideList": [
                    { "Element": { "Ref": "CustomElementValue" },
                    { "Element2": "Value2" },
                    { "Ref": "ListValue" }
                ]
            }
        }

        :param parameters:
        :return:
        """
        def walk(node: Union[Dict, List, AnyStr, int], parent, lookup: dict):
            if isinstance(node, dict) and 'Ref' in node.keys() and len(node.keys()) == 1:  # { "Ref": "someValue" }
                value = lookup.get(node['Ref'], None)
                if value:
                    parent['pointer'][parent['index']] = value
            elif isinstance(node, dict):  # like NoReplaceNeeded2
                for k, n in node.items():
                    walk(n, dict(pointer=node, index=k), lookup)
            elif isinstance(node, list):  # like InsideList
                for i, e in enumerate(node):
                    walk(e, dict(pointer=node, index=i), lookup)
            else:  # like NoReplaceNeeded
                return
        walk(self.node, None, parameters)

