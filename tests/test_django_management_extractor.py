from unittest import mock

from migration_lint.django.extractor.django_management import DjangoManagementExtractor
from migration_lint.source_loader.model import SourceDiff


def test_django_extractor__ok():
    extractor = DjangoManagementExtractor()
    changed_files = [
        SourceDiff(path="documents/migrations/0001_initial.py"),
        SourceDiff(path="documents/models.py"),
        SourceDiff(path="documents/services.py"),
    ]

    with mock.patch(
        "migration_lint.django.extractor.django_management.django.apps.apps.get_app_configs"
    ) as get_app_configs_mock:
        with mock.patch(
            "migration_lint.django.extractor.django_management.call_command"
        ) as call_command_mock:
            call_command_mock.return_value = "ALTER TABLE t DROP COLUMN c;"
            get_app_configs_mock.return_value = []
            metadata = extractor.create_metadata(changed_files)

    assert len(metadata.migrations) == 1
    assert metadata.migrations[0].raw_sql == "ALTER TABLE t DROP COLUMN c;"
    assert metadata.changed_files[0].allowed_with_backward_incompatible is True
    assert metadata.changed_files[1].allowed_with_backward_incompatible is True
    assert metadata.changed_files[2].allowed_with_backward_incompatible is False
