"""This file contains shared fixtures and pytest hooks.

https://docs.pytest.org/en/6.2.x/fixture.html#conftest-py-sharing-fixtures-across-multiple-files
"""

from typing import Iterator

from _pytest.config import Config
from _pytest.nodes import Item
from freezegun import freeze_time
from pytest import fixture
from pytest_mock.plugin import MockerFixture
from typeguard import typechecked
from typeguard.importhook import install_import_hook


def pytest_configure(config: Config) -> None:
    """Initial pytest configuration hook.

    Note:
        We cannot use --typeguard-packages=tests since we currently get the
        following error:

        typeguard cannot check these packages because they are already imported

        When trying to install an import hook for the 'tests' pacakge (i.e.
        install_import_hook('tests')), it breaks pytest's assertion rewriting.
        See the following URL for more information:

        https://docs.pytest.org/en/stable/writing_plugins.html#assertion-rewriting

    See the following URL for more information on this pytest hook:
        https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_configure
    """
    del config

    install_import_hook("bugyi.lib")


def pytest_runtest_call(item: Item) -> None:
    """Called once for each test function.

    See the following URL for more information on this pytest hook:
        https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_runtest_call
    """
    # Decorate every test function [e.g. test_foo()] with typeguard's
    # typechecked() decorator.
    test_func = getattr(item, "obj", None)
    if test_func is not None:
        setattr(item, "obj", typechecked(test_func))


@fixture
def mock_dynamic_log_fields(mocker: MockerFixture) -> None:
    """Mock dynamic fields that may be contained in log records."""
    mocker.patch("logutils.api.getpid", return_value=12345)

    frameinfo = mocker.MagicMock()
    setattr(frameinfo, "function", "fake_function")
    setattr(frameinfo, "lineno", "123")
    mocker.patch(
        "logutils.api.getframeinfo",
        return_value=frameinfo,
    )

    mod = mocker.MagicMock()
    setattr(mod, "__name__", "fake_module")
    mocker.patch("logutils.api.getmodule", return_value=mod)


@fixture(autouse=True, scope="session")
def frozen_time() -> Iterator[None]:
    """Freeze time until our tests are done running."""
    with freeze_time("2021-09-06T15:45:03.585481Z"):
        yield
