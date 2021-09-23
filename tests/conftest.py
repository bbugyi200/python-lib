"""Shared fixture file used by pytest.

https://docs.pytest.org/en/6.2.x/fixture.html#conftest-py-sharing-fixtures-across-multiple-files
"""

from _pytest.config import Config
from typeguard.importhook import install_import_hook


def pytest_configure(config: Config) -> None:
    """Setup typeguard importhooks.

    NOTE: We cannot use --typeguard-packages=tests since we currently get the
    following error:
        typeguard cannot check these packages because they are already imported
    """
    del config

    install_import_hook("tests")
    install_import_hook("bugyi.lib")
