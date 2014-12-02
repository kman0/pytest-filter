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
    parser.addoption(
        '--no-filter', action="store_false", dest="filter", default=True,
        help="disable pytest-filter"
    )
    parser.addini('filter_file', 'Location of filter file')


def pytest_report_header(config, startdir):
    if not config.option.filter:
        print('filter: disabled by --no-filter')
    elif 'filter_file' in config.inicfg:
        print('filter: %s' % config.inicfg['filter_file'])
    else:
        print('filter: "filter_file" key was not found in [pytest] section')


@pytest.mark.trylast
def pytest_configure(config):
    if not config.option.filter:
        return
    if 'filter_file' in config.inicfg:
        filter_path = Path(config.inicfg['filter_file'])
        if not filter_path.isfile():
            raise FileNotFoundError('filter_file: %s' % filter_path)
        config._filter = filter_path


def pytest_collection_modifyitems(session, config, items):
    """ return custom item/collector for a python object in a module, or None.  """
    if not config.option.filter:
        return
    if 'filter_file' not in config.inicfg:
        return

    remaining = []
    deselected = []
    con = configparser.ConfigParser(allow_no_value=True)
    con.read(config._filter)

    xfail_count = 0
    nodes = lambda x: [k if v is None else k+':'+v for k, v in x.items()]

    for colitem in items:
        exclude_test = False
        if 'exclude-prefix' in con.sections():
            for prefix in nodes(con['exclude-prefix']):
                if colitem.nodeid.startswith(prefix):
                    exclude_test = True

        if 'exclude-mark' in con.sections():
            for mark in nodes(con['exclude-mark']):
                if colitem.get_marker(mark):
                    exclude_test = True

        if 'exclude-node' in con.sections():
            if colitem.nodeid in nodes(con['exclude-node']):
                exclude_test = True

        if 'include-prefix' in con.sections():
            for prefix in nodes(con['include-prefix']):
                if colitem.nodeid.startswith(prefix):
                    exclude_test = False

        if 'include-mark' in con.sections():
            for mark in nodes(con['include-mark']):
                if colitem.get_marker(mark):
                    exclude_test = False

        if 'include-node' in con.sections():
            if colitem.nodeid in nodes(con['include-node']):
                exclude_test = False

        if exclude_test:
            deselected.append(colitem)
        else:
            remaining.append(colitem)

        if 'xfail-node' in con.sections() and colitem.nodeid in nodes(con['xfail-node']):
            if "xfail" not in colitem.keywords:
                colitem.add_marker('xfail')
                xfail_count += 1

        # if 'skip-node' in con.sections() and colitem.nodeid in nodes(con['skip-node']):
        #     if "skip" not in colitem.keywords:
        #         colitem.add_marker("skiif")

    print("filter stats -- selected: %s, de-selected: %s, xfail: %s" % (
        len(remaining), len(deselected), xfail_count))

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = remaining
