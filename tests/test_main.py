from __future__ import annotations

from unittest import mock

import pytest
from click.testing import CliRunner

from migration_lint.extractor.django import DjangoExtractor
from migration_lint.main import main
from migration_lint.source_loader.local import LocalLoader


@pytest.mark.parametrize("squawk_config", [[], ["--squawk-config-path=.squawk.toml"]])
def test_main(squawk_config: list):
    runner = CliRunner()

    with mock.patch("migration_lint.main.Analyzer") as analyzer_mock:
        result = runner.invoke(
            main,
            ["--loader=local_git", "--extractor=django", *squawk_config],
        )

    assert result.exit_code == 0, result.stdout
    assert isinstance(analyzer_mock.call_args.kwargs["loader"], LocalLoader)
    assert isinstance(analyzer_mock.call_args.kwargs["extractor"], DjangoExtractor)
