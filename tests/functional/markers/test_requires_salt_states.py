"""
    tests.functional.markers.test_requires_salt_states
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test the ``@pytest.mark.requires_salt_states`` marker
"""
import pytest


@pytest.mark.parametrize(
    "modules",
    [
        ("cmd",),
        ("cmd", "test"),
    ],
)
def test_has_required_salt_state(testdir, modules):
    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.requires_salt_states({})
        def test_one():
            assert True
        """.format(
            ", ".join(repr(module) for module in modules)
        )
    )
    res = testdir.runpytest()
    res.assert_outcomes(passed=1)
    res.stdout.no_fnmatch_line("*PytestUnknownMarkWarning*")


@pytest.mark.parametrize(
    "modules",
    [
        ("cmdmod",),
        ("cmd", "tests"),
    ],
)
def test_missing_required_salt_state(testdir, modules):
    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.requires_salt_states({})
        def test_one():
            assert True
        """.format(
            ", ".join(repr(module) for module in modules)
        )
    )
    res = testdir.runpytest()
    res.assert_outcomes(skipped=1)
    res.stdout.no_fnmatch_line("*PytestUnknownMarkWarning*")


def test_has_required_custom_salt_state(testdir):
    testdir.makepyfile(
        r"""
        import pathlib
        import textwrap
        import pytest
        import logging
        import saltfactories.utils.functional

        log = logging.getLogger(__name__)

        custom_module_name = "bogus"


        @pytest.fixture(scope="session")
        def session_markers_loader(salt_factories):
            minion_id = "session-markers-loader-states"
            root_dir = salt_factories.get_root_dir_for_daemon(minion_id)
            rootfs = root_dir / "rootfs" / "states"
            rootfs.mkdir(parents=True)
            rootfs_states = rootfs / "_states"
            rootfs_states.mkdir(parents=True)
            module_contents = textwrap.dedent('''\
            def echoed(name):
                return {"result": True, "changes": {}, "comment": name, "name": name}
            ''')
            module_path = rootfs_states / "{}.py".format(custom_module_name)
            module_path.write_text(module_contents)
            config_defaults = {
                "root_dir": str(root_dir),
            }
            config_overrides = {
                "file_client": "local",
                "features": {"enable_slsvars_fixes": True},
                "file_roots": {
                    "base": [str(rootfs)]
                }
            }
            factory = salt_factories.get_salt_minion_daemon(
                minion_id, config_defaults=config_defaults, config_overrides=config_overrides,
            )
            loader_instance = saltfactories.utils.functional.Loaders(factory.config.copy())
            ret = loader_instance.states.bogus.echoed("foo")
            assert ret.filtered == {"result": True, "changes": {}, "comment": "foo", "name": "foo"}
            return loader_instance

        @pytest.mark.requires_salt_states(custom_module_name)
        def test_custom_module():
            assert True
        """
    )
    res = testdir.runpytest()
    res.assert_outcomes(passed=1)
    res.stdout.no_fnmatch_line("*PytestUnknownMarkWarning*")


def test_marker_does_not_accept_keyword_argument(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.requires_salt_states("cmd", foo=True)
        def test_one():
            assert True
        """
    )
    res = testdir.runpytest()
    res.assert_outcomes(errors=1)
    res.stdout.fnmatch_lines(
        ["*UsageError: The 'required_salt_states' marker does not accept keyword arguments*"]
    )


def test_marker_only_accepts_string_arguments(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.requires_salt_states(("cmd", "test"))
        def test_one():
            assert True
        """
    )
    res = testdir.runpytest()
    res.assert_outcomes(errors=1)
    res.stdout.fnmatch_lines(
        ["*UsageError: The 'required_salt_states' marker only accepts strings as arguments*"]
    )


def test_marker_errors_with_no_arguments(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.requires_salt_states
        def test_one():
            assert True
        """
    )
    res = testdir.runpytest()
    res.assert_outcomes(errors=1)
    res.stdout.fnmatch_lines(
        [
            "*UsageError: The 'required_salt_states' marker needs at least one state module name to be passed*"
        ]
    )
