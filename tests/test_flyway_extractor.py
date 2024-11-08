from unittest import mock

from migration_lint.extractor.flyway import FlywayExtractor
from migration_lint.source_loader.model import SourceDiff


def test_flyway_extractor__ok():
    extractor = FlywayExtractor()
    changed_files = [
        SourceDiff(path="src/resources/db/migration/v1_some_migration.sql"),
        SourceDiff(path="src/main/Listeners.java"),
        SourceDiff(path="src/main/Listeners.kt"),
    ]

    sql = "ALTER TABLE t DROP COLUMN c;"
    mocked_open = mock.mock_open(read_data=sql)
    with mock.patch("builtins.open", mocked_open):
        metadata = extractor.create_metadata(changed_files)

    assert len(metadata.migrations) == 1
    assert metadata.migrations[0].raw_sql == "ALTER TABLE t DROP COLUMN c;"
    assert metadata.changed_files[0].allowed_with_backward_incompatible is True
    assert metadata.changed_files[1].allowed_with_backward_incompatible is False
    assert metadata.changed_files[2].allowed_with_backward_incompatible is False
