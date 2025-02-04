# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    ArgFormat, DependencyCtxMgr, ModuleHelper, VarMeta
)


def single_lambda_2star(x, y, z):
    return ["piggies=[{0},{1},{2}]".format(x, y, z)]


ARG_FORMATS = dict(
    simple_boolean_true=("--superflag", ArgFormat.BOOLEAN, 0,
                         True, ["--superflag"]),
    simple_boolean_false=("--superflag", ArgFormat.BOOLEAN, 0,
                          False, []),
    simple_boolean_none=("--superflag", ArgFormat.BOOLEAN, 0,
                         None, []),
    single_printf=("--param=%s", ArgFormat.PRINTF, 0,
                   "potatoes", ["--param=potatoes"]),
    single_printf_no_substitution=("--param", ArgFormat.PRINTF, 0,
                                   "potatoes", ["--param"]),
    single_printf_none=("--param=%s", ArgFormat.PRINTF, 0,
                        None, []),
    multiple_printf=(["--param", "free-%s"], ArgFormat.PRINTF, 0,
                     "potatoes", ["--param", "free-potatoes"]),
    single_format=("--param={0}", ArgFormat.FORMAT, 0,
                   "potatoes", ["--param=potatoes"]),
    single_format_none=("--param={0}", ArgFormat.FORMAT, 0,
                        None, []),
    single_format_no_substitution=("--param", ArgFormat.FORMAT, 0,
                                   "potatoes", ["--param"]),
    multiple_format=(["--param", "free-{0}"], ArgFormat.FORMAT, 0,
                     "potatoes", ["--param", "free-potatoes"]),
    multiple_format_none=(["--param", "free-{0}"], ArgFormat.FORMAT, 0,
                          None, []),
    single_lambda_0star=((lambda v: ["piggies=[{0},{1},{2}]".format(v[0], v[1], v[2])]), None, 0,
                         ['a', 'b', 'c'], ["piggies=[a,b,c]"]),
    single_lambda_0star_none=((lambda v: ["piggies=[{0},{1},{2}]".format(v[0], v[1], v[2])]), None, 0,
                              None, []),
    single_lambda_1star=((lambda a, b, c: ["piggies=[{0},{1},{2}]".format(a, b, c)]), None, 1,
                         ['a', 'b', 'c'], ["piggies=[a,b,c]"]),
    single_lambda_1star_none=((lambda a, b, c: ["piggies=[{0},{1},{2}]".format(a, b, c)]), None, 1,
                              None, []),
    single_lambda_2star=(single_lambda_2star, None, 2,
                         dict(z='c', x='a', y='b'), ["piggies=[a,b,c]"]),
    single_lambda_2star_none=(single_lambda_2star, None, 2,
                              None, []),
)
ARG_FORMATS_IDS = sorted(ARG_FORMATS.keys())


@pytest.mark.parametrize('fmt, style, stars, value, expected',
                         (ARG_FORMATS[tc] for tc in ARG_FORMATS_IDS),
                         ids=ARG_FORMATS_IDS)
def test_arg_format(fmt, style, stars, value, expected):
    af = ArgFormat('name', fmt, style, stars)
    actual = af.to_text(value)
    print("formatted string = {0}".format(actual))
    assert actual == expected


ARG_FORMATS_FAIL = dict(
    int_fmt=(3, None, 0, "", [""]),
    bool_fmt=(True, None, 0, "", [""]),
)
ARG_FORMATS_FAIL_IDS = sorted(ARG_FORMATS_FAIL.keys())


@pytest.mark.parametrize('fmt, style, stars, value, expected',
                         (ARG_FORMATS_FAIL[tc] for tc in ARG_FORMATS_FAIL_IDS),
                         ids=ARG_FORMATS_FAIL_IDS)
def test_arg_format_fail(fmt, style, stars, value, expected):
    with pytest.raises(TypeError):
        af = ArgFormat('name', fmt, style, stars)
        actual = af.to_text(value)
        print("formatted string = {0}".format(actual))


def test_dependency_ctxmgr():
    ctx = DependencyCtxMgr("POTATOES", "Potatoes must be installed")
    with ctx:
        import potatoes_that_will_never_be_there
    print("POTATOES: ctx.text={0}".format(ctx.text))
    assert ctx.text == "Potatoes must be installed"
    assert not ctx.has_it

    ctx = DependencyCtxMgr("POTATOES2")
    with ctx:
        import potatoes_that_will_never_be_there_again
    assert not ctx.has_it
    print("POTATOES2: ctx.text={0}".format(ctx.text))
    assert ctx.text.startswith("No module named")
    assert "potatoes_that_will_never_be_there_again" in ctx.text

    ctx = DependencyCtxMgr("TYPING")
    with ctx:
        import sys
    assert ctx.has_it


def test_variable_meta():
    meta = VarMeta()
    assert meta.output is True
    assert meta.diff is False
    assert meta.value is None
    meta.set_value("abc")
    assert meta.initial_value == "abc"
    assert meta.value == "abc"
    assert meta.diff_result is None
    meta.set_value("def")
    assert meta.initial_value == "abc"
    assert meta.value == "def"
    assert meta.diff_result is None


def test_variable_meta_diff():
    meta = VarMeta(diff=True)
    assert meta.output is True
    assert meta.diff is True
    assert meta.value is None
    meta.set_value("abc")
    assert meta.initial_value == "abc"
    assert meta.value == "abc"
    assert meta.diff_result is None
    meta.set_value("def")
    assert meta.initial_value == "abc"
    assert meta.value == "def"
    assert meta.diff_result == {"before": "abc", "after": "def"}
    meta.set_value("ghi")
    assert meta.initial_value == "abc"
    assert meta.value == "ghi"
    assert meta.diff_result == {"before": "abc", "after": "ghi"}


def test_vardict():
    vd = ModuleHelper.VarDict()
    vd.set('a', 123)
    assert vd['a'] == 123
    assert vd.a == 123
    assert 'a' in vd._meta
    assert vd.meta('a').output is True
    assert vd.meta('a').diff is False
    assert vd.meta('a').change is False
    vd['b'] = 456
    vd.set_meta('a', diff=True, change=True)
    vd.set_meta('b', diff=True, output=False)
    vd['c'] = 789
    vd['a'] = 'new_a'
    vd['c'] = 'new_c'
    assert vd.a == 'new_a'
    assert vd.c == 'new_c'
    assert vd.output() == {'a': 'new_a', 'c': 'new_c'}
    assert vd.diff() == {'before': {'a': 123}, 'after': {'a': 'new_a'}}, "diff={0}".format(vd.diff())
