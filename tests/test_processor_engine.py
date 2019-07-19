#!/usr/bin/env python
import pytest

from cfmacro.core.engine import ProcessorEngine
from cfmacro.processors import SgProcessor

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


def test_register_processor_wrong_type():
    class Test(object):
        pass

    pe = ProcessorEngine()
    with pytest.raises(ValueError) as excinfo:
        pe.register_processor(Test)
    assert 'Not a valid object' in str(excinfo.value)


def test_register_processor_sg_processor_is_registered():
    pe = ProcessorEngine()
    pe.register_processor(SgProcessor)
    assert SgProcessor in pe.processors


def test_processor_engine_tag_is_present():
    pe = ProcessorEngine()
    pe.register_processor(SgProcessor)
    assert SgProcessor.tag in pe.processor_map.keys()
