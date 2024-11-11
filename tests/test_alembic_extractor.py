from unittest import mock

from migration_lint.extractor.alembic import AlembicExtractor
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
            "UPDATE alembic_version SET version_num='fbea801d4464'".encode("utf-8")
        )
        metadata = extractor.create_metadata(changed_files)

    assert len(metadata.migrations) == 1
    assert metadata.migrations[0].raw_sql == "ALTER TABLE t DROP COLUMN c;"
    assert metadata.changed_files[0].allowed_with_backward_incompatible is True
    assert metadata.changed_files[1].allowed_with_backward_incompatible is True
    assert metadata.changed_files[2].allowed_with_backward_incompatible is False
