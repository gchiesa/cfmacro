from typing import Dict, List

from ...cloudformation.elements import CloudFormationResource, CloudFormationTemplate

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class IncludeModuleException(Exception):
    pass


class IncludeModule(object):

    def __init__(self, template: CloudFormationTemplate):
        self._cf = template
        self.custom_parameters = {}

    def with_parameters(self, parameters: Dict):
        self.custom_parameters = parameters
        return self

    def _prepare_parameters(self) -> Dict:
        """
        build the final parameters dict using the custom parameters and the defaults from the template.
        If some default is missing it will raise exception

        :return: dict of parameters
        """
        result = {}
        for param_name, param_node in self._cf.parameters.items():
            result[param_name] = param_node.get('Default', None)
            if param_name in self.custom_parameters.keys():
                result[param_name] = self.custom_parameters[param_name]
            if result[param_name] is None:
                raise IncludeModuleException(f'Missing default of parameter for {param_name}')
        return result

    def generate_resources(self) -> List[CloudFormationResource]:
        parameters = self._prepare_parameters()
        self._cf.update_refs_from_dict(parameters)
        return self._cf.resources
