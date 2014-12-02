# -*- coding: utf-8 -*-
"""
pytest-filter tests
*******************

"""
import pytest

pytest_plugins = 'pytester'
from pprint import pprint

__author__ = 'M'

five_tests = """
import pytest
def test_pass1(): assert 1
def test_pass2(): assert 1
def test_pass3(): assert 1
def test_pass4(): assert 1
def test_pass5(): assert 1
"""


def init_pass(testdir):
    testdir.makepyfile("""
    import pytest
    def test_pass(): assert 1
    """)


def init_tests(testdir):
    testdir.tmpdir.ensure("test_d1/test_m1.py").write(five_tests)


def init_multiple_tests(testdir):

    testdir.tmpdir.ensure("test_d1/test_m1.py").write(five_tests)
    testdir.tmpdir.ensure("test_d1/test_m2.py").write(five_tests)
    testdir.tmpdir.ensure("test_d2/test_m3.py").write(five_tests)
    testdir.tmpdir.ensure("test_d3/test_m4.py").write("""
import pytest
def test_pass(): assert 1
def test_fail(): assert 0
@pytest.mark.skipif(True, reason="skip")
def test_skip(): pass
@pytest.mark.xfail
def test_xfail(): assert 0
@pytest.mark.xfail
def test_xpass(): assert 1
""")


def init_ini(testdir):
    testdir.tmpdir.ensure("pytest.ini").write("""[pytest]
filter_file=filter.ini""")


def init_filter(testdir, **kwargs):
    testdir.tmpdir.ensure("filter.ini").write("\n".join([
        "\n[exclude-prefix]\n%s" % '\n'.join(kwargs['exclude_prefix'] if 'exclude_prefix' in kwargs else []),
        "\n[exclude-mark]\n%s" % '\n'.join(kwargs['exclude_mark']if 'exclude_mark' in kwargs else []),
        "\n[exclude-node]\n%s" % '\n'.join(kwargs['exclude_node']if 'exclude_node' in kwargs else []),
        "\n[include-prefix]\n%s" % '\n'.join(kwargs['include_prefix']if 'include_prefix' in kwargs else []),
        "\n[include-mark]\n%s" % '\n'.join(kwargs['include_mark']if 'include_mark' in kwargs else []),
        "\n[include-node]\n%s" % '\n'.join(kwargs['include_node']if 'include_node' in kwargs else []),
        "\n[xfail-node]\n%s" % '\n'.join(kwargs['xfail_node']if 'xfail_node' in kwargs else [])
        ])
    )


# # Tests
def test_no_filter(testdir):
    init_pass(testdir)
    result = testdir.runpytest('--no-filter', testdir.tmpdir)
    assert result.ret == 0
    result.stdout.fnmatch_lines_random("*filter: disabled by --no-filter*")


def test_no_configure_print(testdir):
    init_pass(testdir)
    result = testdir.runpytest(testdir.tmpdir)
    assert result.ret == 0
    result.stdout.fnmatch_lines_random(r'*filter: "filter_file" key was not found in [pytest? section*')


def test_filter_path_file_not_found(testdir):
    init_ini(testdir)
    init_pass(testdir)
    result = testdir.runpytest(testdir.tmpdir)
    assert result.ret == 3
    result.stdout.fnmatch_lines_random("*FileNotFoundError: filter_file: filter.ini*")


def test_filter_path_print(testdir):
    init_ini(testdir)
    init_pass(testdir)
    testdir.tmpdir.ensure("filter.ini").write("""[pytest]""")
    result = testdir.runpytest(testdir.tmpdir)
    assert result.ret == 0
    result.stdout.fnmatch_lines_random("*filter: filter.ini*")


def test_filter_stats_print(testdir):
    init_ini(testdir)
    init_pass(testdir)
    testdir.tmpdir.ensure("filter.ini").write("""[pytest]""")
    result = testdir.runpytest(testdir.tmpdir)
    assert result.ret == 0
    result.stdout.fnmatch_lines_random("*filter stats -- selected: 1, de-selected: 0, xfail: 0*")


def test_select_20(testdir):
    init_ini(testdir)
    init_tests(testdir)
    init_filter(testdir)
    # pprint(testdir)
    init_filter(testdir)
    result = testdir.runpytest('--collect-only', testdir.tmpdir)
    # pprint(result.stdout.lines)
    assert result.ret == 0
    result.stdout.fnmatch_lines_random("*filter stats -- selected: 5, de-selected: 0, xfail: 0*")


def test_exclude_one_node(testdir):
    init_ini(testdir)
    init_tests(testdir)
    # pprint(testdir)
    init_filter(testdir, exclude_node=['test_d1/test_m1.py::test_pass3'])
    result = testdir.runpytest('--collect-only', testdir.tmpdir)
    # pprint(result.stdout.lines)
    assert result.ret == 0
    result.stdout.fnmatch_lines_random("*filter stats -- selected: 4, de-selected: 1, xfail: 0*")


def test_exclude_two_nodes(testdir):
    init_ini(testdir)
    init_tests(testdir)
    init_filter(testdir, exclude_node=['''
test_d1/test_m1.py:
    test_pass3
    test_pass4'''])
    result = testdir.runpytest('--collect-only', testdir.tmpdir)
    # pprint(result.stdout.lines)
    assert result.ret == 0
    with pytest.raises(ValueError) as exc:
        result.stdout.fnmatch_lines_random("*Function 'test_pass3'*")
    assert 'not found in output' in exc.value.args[0]
    assert 'test_pass3' in exc.value.args[0]
    with pytest.raises(ValueError) as exc:
        result.stdout.fnmatch_lines_random("*Function 'test_pass4'*")
    assert 'not found in output' in exc.value.args[0]
    assert 'test_pass4' in exc.value.args[0]


def test_exclude_all(testdir):
    init_ini(testdir)
    init_tests(testdir)
    init_filter(testdir, exclude_prefix=["test_d1/test_m1.py::test_pass"])
    result = testdir.runpytest('--collect-only', testdir.tmpdir)
    assert result.ret == 0

    with pytest.raises(ValueError) as exc:
        result.stdout.fnmatch_lines_random("*Function 'test_pass1'*")
    assert 'not found in output' in exc.value.args[0]
    assert 'test_pass1' in exc.value.args[0]
    with pytest.raises(ValueError) as exc:
        result.stdout.fnmatch_lines_random("*Function 'test_pass2'*")
    assert 'not found in output' in exc.value.args[0]
    assert 'test_pass2' in exc.value.args[0]
    with pytest.raises(ValueError) as exc:
        result.stdout.fnmatch_lines_random("*Function 'test_pass3'*")
    assert 'not found in output' in exc.value.args[0]
    assert 'test_pass3' in exc.value.args[0]
    with pytest.raises(ValueError) as exc:
        result.stdout.fnmatch_lines_random("*Function 'test_pass4'*")
    assert 'not found in output' in exc.value.args[0]
    assert 'test_pass4' in exc.value.args[0]
    with pytest.raises(ValueError) as exc:
        result.stdout.fnmatch_lines_random("*Function 'test_pass5'*")
    assert 'not found in output' in exc.value.args[0]
    assert 'test_pass5' in exc.value.args[0]
    result.stdout.fnmatch_lines_random("*5 deselected*")
    result.stdout.fnmatch_lines_random('*filter stats -- selected: 0, de-selected: 5, xfail: 0')


def test_exclude_all_include_two_nodes(testdir):
    init_ini(testdir)
    init_tests(testdir)
    init_filter(testdir, include_node=['''
test_d1/test_m1.py:
    test_pass3
    test_pass4'''], exclude_prefix=["test_d1/test_m1.py::test_pass"])
    result = testdir.runpytest('--collect-only', testdir.tmpdir)
    assert result.ret == 0
    with pytest.raises(ValueError) as exc:
        result.stdout.fnmatch_lines_random("*Function 'test_pass1'*")
    assert 'not found in output' in exc.value.args[0]
    assert 'test_pass1' in exc.value.args[0]
    with pytest.raises(ValueError) as exc:
        result.stdout.fnmatch_lines_random("*Function 'test_pass2'*")
    assert 'not found in output' in exc.value.args[0]
    assert 'test_pass2' in exc.value.args[0]
    with pytest.raises(ValueError) as exc:
        result.stdout.fnmatch_lines_random("*Function 'test_pass5'*")
    assert 'not found in output' in exc.value.args[0]
    assert 'test_pass5' in exc.value.args[0]
    result.stdout.fnmatch_lines_random("*Function 'test_pass3'*")
    result.stdout.fnmatch_lines_random("*Function 'test_pass4'*")
    result.stdout.fnmatch_lines_random("*Module 'test_d1/test_m1.py'*")

    result.stdout.fnmatch_lines_random("*3 deselected*")
    result.stdout.fnmatch_lines_random('*filter stats -- selected: 2, de-selected: 3, xfail: 0')


def test_exclude_all_include_prefix(testdir):
    init_ini(testdir)
    init_tests(testdir)
    init_filter(testdir, exclude_prefix=["test_d1/test_m1.py::test_pass"],
                include_prefix=["test_d1/test_m1.py::test_pass"])
    result = testdir.runpytest('--collect-only', testdir.tmpdir)
    assert result.ret == 0

    result.stdout.fnmatch_lines_random("*Module 'test_d1/test_m1.py'*")
    result.stdout.fnmatch_lines_random("*Function 'test_pass1'*")
    result.stdout.fnmatch_lines_random("*Function 'test_pass2'*")
    result.stdout.fnmatch_lines_random("*Function 'test_pass3'*")
    result.stdout.fnmatch_lines_random("*Function 'test_pass4'*")
    result.stdout.fnmatch_lines_random("*Function 'test_pass5'*")
    result.stdout.fnmatch_lines_random('*filter stats -- selected: 5, de-selected: 0, xfail: 0')
