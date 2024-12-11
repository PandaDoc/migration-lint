from typing import Union
from unittest.mock import patch

import pytest

from migration_lint.analyzer.squawk import SquawkLinter

FAKE_STATEMENT = "fake sql"


@pytest.mark.parametrize(
    "platform, result",
    [("linux", "squawk-linux-x86"), ("darwin", "squawk-darwin-arm64")],
)
@patch("migration_lint.__path__", ["migration_lint_path"])
def test_platform(platform: str, result: str):
    with patch("sys.platform", platform):
        linter = SquawkLinter()
        assert f"migration_lint_path/bin/{result}" == linter.squawk


def test_unsupported_platform():
    with patch("sys.platform", "win32"):
        with pytest.raises(RuntimeError, match="unsupported platform: win32"):
            SquawkLinter()


@pytest.mark.parametrize(
    "config_path, result_flags",
    [(None, ""), (".squawk.toml", "--config=.squawk.toml")],
    ids=["Without config", "With config"],
)
@patch("migration_lint.__path__", ["path"])
@patch("sys.platform", "linux")
def test_squawk_command(config_path: Union[str, None], result_flags: str):
    ignored_rules = ["ignored-rule"]

    with patch.object(
        SquawkLinter, "ignored_rules", new_callable=lambda: ignored_rules
    ):
        linter = SquawkLinter(config_path)

        result = linter.squawk_command(FAKE_STATEMENT)

    expected_result = f"path/bin/squawk-linux-x86 --exclude=ignored-rule {result_flags}"
    assert result == expected_result.strip()
