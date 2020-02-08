# -*- coding: utf-8 -*-
"""
tests.functional.utils.processes.test_factory_script_base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test saltfactories.utils.processes.FactoryScriptBase
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys

import pytest

from saltfactories.utils.processes import FactoryScriptBase


@pytest.mark.parametrize("exitcode", [0, 1, 3, 9, 40, 120])
def test_exitcode(exitcode, tempfiles):
    shell = FactoryScriptBase(sys.executable)
    script = tempfiles.makepyfile(
        """
        # -*- coding: utf-8 -*-
        import time
        time.sleep(0.125)
        exit({})
        """.format(
            exitcode
        )
    )
    result = shell.run(script)
    assert result.exitcode == exitcode


def test_timeout_defined_on_class_instantiation(tempfiles):
    def raise_exception(msg):
        raise RuntimeError(msg)

    shell = FactoryScriptBase(sys.executable, default_timeout=0.5, fail_callable=raise_exception)
    script = tempfiles.makepyfile(
        """
        # -*- coding: utf-8 -*-
        import time
        time.sleep(1)
        exit(0)
        """
    )
    with pytest.raises(RuntimeError):
        shell.run(script)


def test_timeout_defined_run(tempfiles):
    def raise_exception(msg):
        raise RuntimeError(msg)

    shell = FactoryScriptBase(sys.executable, fail_callable=raise_exception)
    script = tempfiles.makepyfile(
        """
        # -*- coding: utf-8 -*-
        import time
        time.sleep(0.5)
        exit(0)
        """
    )
    result = shell.run(script)
    assert result.exitcode == 0

    script = tempfiles.makepyfile(
        """
        # -*- coding: utf-8 -*-
        import time
        time.sleep(0.5)
        exit(0)
        """
    )
    with pytest.raises(RuntimeError):
        shell.run(script, _timeout=0.1)


@pytest.mark.parametrize(
    "input_str,expected_object",
    [
        # Good JSON
        ('{"a": "a", "1": 1}', {"a": "a", "1": 1}),
        # Bad JSON
        ("{'a': 'a', '1': 1}", None),
    ],
)
def test_json_output(input_str, expected_object, tempfiles):
    shell = FactoryScriptBase(sys.executable)
    script = tempfiles.makepyfile(
        """
        # -*- coding: utf-8 -*-
        import sys
        sys.stdout.write('''{}''')
        exit(0)
        """.format(
            input_str
        )
    )
    result = shell.run(script)
    assert result.exitcode == 0
    if result.json:
        assert result.json == expected_object
    assert result.stdout == input_str


def test_stderr_output(tempfiles):
    input_str = "Thou shalt not exit cleanly"
    shell = FactoryScriptBase(sys.executable)
    script = tempfiles.makepyfile(
        """
        # -*- coding: utf-8 -*-
        exit("{}")
        """.format(
            input_str
        )
    )
    result = shell.run(script)
    assert result.exitcode == 1
    assert result.stderr == input_str + "\n"
