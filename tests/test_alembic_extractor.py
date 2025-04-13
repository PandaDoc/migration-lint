import subprocess
from unittest import mock

import pytest

from migration_lint.extractor.alembic import AlembicExtractor, os
from migration_lint.source_loader.model import SourceDiff


def test_alembic_extractor__ok():
    extractor = AlembicExtractor()
    changed_files = [
        SourceDiff(path="src/db/migrations/versions/202202151945_fbea801d4464_auto.py"),
        SourceDiff(path="src/tables.py"),
        SourceDiff(path="src/services.py"),
    ]

    with mock.patch(
        "migration_lint.extractor.alembic.subprocess.check_output"
    ) as subprocess_mock:
        subprocess_mock.return_value = (
            "command\n"
            "CREATE TABLE t;\n"
            "UPDATE alembic_version SET version_num='000000000000'\n"
            "-- Running upgrade  -> fbea801d4464\n"
            "ALTER TABLE t DROP COLUMN c;\n"
            "INSERT INTO alembic_version (version_num) VALUES (fbea801d4464) RETURNING alembic_version.version_num\n"
            "UPDATE alembic_version SET version_num='fbea801d4464'".encode("utf-8")
        )
        metadata = extractor.create_metadata(changed_files)

    assert len(metadata.migrations) == 1
    assert metadata.migrations[0].raw_sql == "ALTER TABLE t DROP COLUMN c;"
    assert metadata.changed_files[0].allowed_with_backward_incompatible is True
    assert metadata.changed_files[1].allowed_with_backward_incompatible is True
    assert metadata.changed_files[2].allowed_with_backward_incompatible is False


@pytest.mark.parametrize(
    "command,expected_command",
    [
        (None, "make sqlmigrate"),
        ("alembic upgrade head --sql", "alembic upgrade head --sql"),
    ],
)
def test_alembic_extractor_command__ok(command, expected_command):
    extractor = AlembicExtractor(alembic_command=command)
    changed_files = [
        SourceDiff(path="src/db/migrations/versions/202202151945_fbea801d4464_auto.py"),
    ]

    with mock.patch(
        "migration_lint.extractor.alembic.subprocess.check_output"
    ) as subprocess_mock:
        subprocess_mock.return_value = "-- Running upgrade fbea801d4465 -> fbea801d4464\nCREATE TABLE t (id serial)".encode(
            "utf-8"
        )
        extractor.create_metadata(changed_files)
        subprocess_mock.assert_called_once_with(expected_command.split())


def test_alembic_extractor_path__ok():
    changed_files = [
        SourceDiff(path="src/db/random/path/202202151945_fbea801d4464_auto.py"),
    ]

    with mock.patch(
        "migration_lint.extractor.alembic.subprocess.check_output"
    ) as subprocess_mock, mock.patch.dict(
        os.environ,
        {"MIGRATION_LINT_ALEMBIC_MIGRATIONS_PATH": "/random/path"},
        clear=True,
    ):
        extractor = AlembicExtractor()
        subprocess_mock.return_value = "-- Running upgrade fbea801d4465 -> fbea801d4464\nCREATE TABLE t (id serial)".encode(
            "utf-8"
        )
        metadata = extractor.create_metadata(changed_files)

    assert len(metadata.migrations) == 1
    assert metadata.changed_files[0].allowed_with_backward_incompatible is True


def test_alembic_extractor__error():
    extractor = AlembicExtractor()
    changed_files = [
        SourceDiff(path="src/db/migrations/versions/202202151945_fbea801d4464_auto.py"),
        SourceDiff(path="src/tables.py"),
        SourceDiff(path="src/services.py"),
    ]

    with mock.patch(
        "migration_lint.extractor.alembic.subprocess.check_output",
        side_effect=subprocess.CalledProcessError(returncode=1, cmd="make sqlmigrate"),
    ):
        with pytest.raises(subprocess.CalledProcessError):
            extractor.create_metadata(changed_files)
