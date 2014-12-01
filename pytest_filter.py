# -*- coding: utf-8 -*-
"""
pytest-filter
*************

"""

from __future__ import print_function

import os
import sys
import time
from path import Path
import pytest
import configparser


def pytest_addoption(parser):
    parser.addini('filter_file', 'Location of filter file')


@pytest.mark.trylast
def pytest_configure(config):
    if 'filter_file' in config.inicfg:
        filter_path = Path(config.inicfg['filter_file'])
        if not filter_path.isfile():
            raise FileNotFoundError('filter_file: %s' % filter_path)

        config._filter = filter_path
        config.pluginmanager.register(config._filter)


def pytest_unconfigure(config):
    """un configure the mf_testlink framework plugin"""
    _filter = getattr(config, '_filter', None)
    if _filter:
        del config._filter
        config.pluginmanager.unregister(_filter)

