# -*- coding: utf-8 -*-

from .core.engine import ProcessorEngine
from .core.template import TemplateProcessor
from .processors import SgProcessor


def lambda_handler(event, context):
    """
    Implement a core handler for security groups ingress / egress


    :param event:
    :param context:
    :return:
    """
    print(f'event received: {event}')
    processor_engine = ProcessorEngine()
    processor_engine.register_processor(SgProcessor)
    template_processor = TemplateProcessor(processor_engine)
    result = template_processor.process(fragment=event['fragment'],
                                        template_params=event['templateParameterValues']).to_dict()
    print(f'event processed. Result: \n{result}')
    return {
        "requestId": event['requestId'],
        "status": "success",
        "fragment": result
    }

