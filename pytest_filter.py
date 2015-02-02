# -*- coding: utf-8 -*-
"""
pytest-filter
*************

"""

from __future__ import print_function

import os
import sys
if sys.version_info[0] < 3:
    import ConfigParser as configparser
    configparser.ConfigParser = configparser.SafeConfigParser
else:
    import configparser

import pytest
from path import Path


def pytest_addoption(parser):
    parser.addoption(
        '--no-filter', action="store_false", dest="filter", default=True,
        help="disable pytest-filter"
    )
    parser.addoption(
        '--filter-exclude-all', action="store_true", dest="filter_exclude_all", default=False,
        help="Excludes all selected tests when true"
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

    remaining = []
    deselected = []
    xfail_count = 0

    filter_map = {
        'exclude-mark': set(),
        'include-mark': set(),
        'exclude-node': set(),
        'include-node': set(),
        'exclude-prefix': set(),
        'include-prefix': set(),
        'xfail-node': set()
    }
    if config.option.filter_exclude_all:
        config.hook.pytest_deselected(items=items)
        items[:] = remaining

    if 'filter_file' in config.inicfg:
        con = configparser.ConfigParser(allow_no_value=True)
        con.read(config._filter)

        # add marks
        for section in ['exclude-mark', 'include-mark']:
            filter_map[section] = set()
            if section in con.sections():
                for mark in con['exclude-mark']:
                    filter_map[section].add(mark.strip())

        # add node ids
        for section in ['exclude-node', 'include-node', 'exclude-prefix', 'include-prefix', 'xfail-node']:
            filter_map[section] = set()
            if section in con.sections():
                for key, val in con[section].items():
                    if not val:
                        filter_map[section] = key
                    else:
                        for v in val.strip().split('\n'):
                            if v.startswith('::'):
                                deli = ""
                            elif v.startswith(':'):
                                deli = ":"
                            else:
                                deli = "::"
                            filter_map[section].add(key + deli + v)

        for colitem in items:
            # print(colitem.nodeid)
            # exclude all tests when config option is set
            exclude_test = False
            section = 'exclude-prefix'
            if section in filter_map:
                for prefix in filter_map[section]:
                    if colitem.nodeid.startswith(prefix):
                        exclude_test = True

            section = 'exclude-mark'
            if section in filter_map:
                for mark in filter_map[section]:
                    if colitem.get_marker(mark):
                        exclude_test = True

            section = 'exclude-node'
            if section in filter_map:
                if colitem.nodeid in filter_map[section]:
                    exclude_test = True

            section = 'include-prefix'
            if section in filter_map:
                for prefix in filter_map[section]:
                    if colitem.nodeid.startswith(prefix):
                        exclude_test = False

            section = 'include-mark'
            if section in filter_map:
                for mark in filter_map[section]:
                    if colitem.get_marker(mark):
                        exclude_test = False

            section = 'include-node'
            if section in filter_map:
                if colitem.nodeid in filter_map[section]:
                    exclude_test = False

            if exclude_test:
                deselected.append(colitem)
            else:
                remaining.append(colitem)

            section = 'xfail-node'
            if section in filter_map and colitem.nodeid in filter_map[section]:
                if "xfail" not in colitem.keywords:
                    colitem.add_marker('xfail')
                    xfail_count += 1

            section = 'skip-node'
            if section in filter_map and colitem.nodeid in filter_map[section]:
                print('ERROR: skip-node is not yet implemented!')
                pass
            #     if "skip" not in colitem.keywords:
            #         colitem.add_marker("skiif")

        print("filter stats -- selected: %s, de-selected: %s, xfail: %s" % (
            len(remaining), len(deselected), xfail_count))

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = remaining
