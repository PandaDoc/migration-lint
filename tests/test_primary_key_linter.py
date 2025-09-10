from unittest.mock import patch

import pytest

from migration_lint.analyzer.primary_key import PrimaryKeyLinter


@pytest.mark.parametrize(
    "sql, has_pk",
    [
        ("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100))", True),
        ("CREATE TABLE users (id INT, name VARCHAR(100), PRIMARY KEY (id))", True),
        ("CREATE TABLE users (id INT primary key)", True),  # case insensitive
        ("CREATE TABLE users (id INT, name VARCHAR(100))", False),
        ("CREATE TABLE logs (message TEXT, created_at TIMESTAMP)", False),
    ],
)
def test_sql_has_primary_key(sql: str, has_pk: bool):
    linter = PrimaryKeyLinter()
    assert linter._sql_has_primary_key(sql) == has_pk


@pytest.mark.parametrize(
    "sql, is_create_table",
    [
        ("CREATE TABLE users (id INT, name VARCHAR(100))", True),
        ("create table products (id serial, name text)", True),
        ("CREATE TABLE IF NOT EXISTS categories (id INT)", True),
        ("ALTER TABLE users ADD COLUMN email VARCHAR(255)", False),
        ("DROP TABLE users", False),
        ("SELECT * FROM users", False),
    ],
)
def test_is_create_table_statement(sql: str, is_create_table: bool):
    linter = PrimaryKeyLinter()
    assert linter._is_create_table_statement(sql) == is_create_table


@patch('migration_lint.analyzer.primary_key.classify_migration')
@patch('migration_lint.analyzer.primary_key.logger')
def test_lint_dry_run_mode_missing_pk(mock_logger, mock_classify):
    """Test dry-run mode logs warnings but returns no errors."""
    mock_classify.return_value = [
        ("CREATE TABLE users (id INT, name VARCHAR(100))", "CREATE_TABLE"),
    ]

    linter = PrimaryKeyLinter(dry_run=True)
    errors = linter.lint("CREATE TABLE users (id INT, name VARCHAR(100))", [])

    assert errors == []
    mock_logger.info.assert_any_call(
        "\x1b[33;21m\n🔍 Primary Key Check (dry-run mode):\x1b[0m"
    )


@patch('migration_lint.analyzer.primary_key.classify_migration')
def test_lint_strict_mode_missing_pk(mock_classify):
    """Test strict mode returns errors for missing primary keys."""
    mock_classify.return_value = [
        ("CREATE TABLE users (id INT, name VARCHAR(100))", "CREATE_TABLE"),
    ]

    linter = PrimaryKeyLinter(dry_run=False)
    errors = linter.lint("CREATE TABLE users (id INT, name VARCHAR(100))", [])

    assert len(errors) == 1
    assert "Table 'users' is created without a primary key" in errors[0]


@patch('migration_lint.analyzer.primary_key.classify_migration')
@patch('migration_lint.analyzer.primary_key.logger')
def test_lint_all_tables_have_pk(mock_logger, mock_classify):
    """Test when all tables have primary keys."""
    mock_classify.return_value = [
        ("CREATE TABLE users (id INT PRIMARY KEY)", "CREATE_TABLE"),
    ]

    linter = PrimaryKeyLinter()
    errors = linter.lint("CREATE TABLE users (id INT PRIMARY KEY)", [])

    assert errors == []
    expected_msg = (
        "\x1b[1;34m✅ Primary Key Check: All created tables "
        "have primary keys.\x1b[0m"
    )
    mock_logger.info.assert_called_with(expected_msg)


@patch('migration_lint.analyzer.primary_key.classify_migration')
@patch('migration_lint.analyzer.primary_key.logger')
def test_lint_exception_handling(mock_logger, mock_classify):
    """Test graceful exception handling."""
    mock_classify.side_effect = Exception("Classification failed")

    linter = PrimaryKeyLinter()
    errors = linter.lint("CREATE TABLE users (id INT)", [])

    assert errors == []
    expected_msg = (
        "\x1b[33;21mPrimary Key Check: Could not analyze SQL - "
        "Classification failed\x1b[0m"
    )
    mock_logger.info.assert_called_with(expected_msg)
