from unittest import mock

from migration_lint.extractor.django import DjangoExtractor
from migration_lint.source_loader.model import SourceDiff


def test_django_extractor__ok():
    extractor = DjangoExtractor()
    changed_files = [
        SourceDiff(path="documents/migrations/0001_initial.py"),
        SourceDiff(path="documents/models.py"),
        SourceDiff(path="documents/services.py"),
    ]

    with mock.patch(
        "migration_lint.extractor.django.subprocess.check_output"
    ) as subprocess_mock:
        subprocess_mock.return_value = (
            "command\nMonkeypatching..\nALTER TABLE t DROP COLUMN c;".encode("utf-8")
        )
        metadata = extractor.create_metadata(changed_files)

    assert len(metadata.migrations) == 1
    assert metadata.migrations[0].raw_sql == "ALTER TABLE t DROP COLUMN c;"
    assert metadata.changed_files[0].allowed_with_backward_incompatible is True
    assert metadata.changed_files[1].allowed_with_backward_incompatible is True
    assert metadata.changed_files[2].allowed_with_backward_incompatible is False
