#!/usr/bin/env python
from .base import ResourceProcessor

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


class ProcessorEngine(object):
    def __init__(self):
        self.processors = []
        self.processor_map = {}

    def register_processor(self, processor):
        if not issubclass(processor, ResourceProcessor):
            raise ValueError('cannot register core. Not a valid object')
        self.processors.append(processor)
        self._update_processor_map()

    def _update_processor_map(self):
        for processor in self.processors:
            self.processor_map[processor.tag] = processor


__all__ = [
    ProcessorEngine
]
