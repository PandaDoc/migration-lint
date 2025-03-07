import pytest as pytest

from migration_lint.sql.constants import StatementType
from migration_lint.sql.parser import classify_migration


@pytest.mark.parametrize(
    "statement,expected_type",
    [
        (
            "CREATE INDEX CONCURRENTLY idx ON table_name (column_name);",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        ("CREATE INDEX idx ON table_name (column_name);", StatementType.RESTRICTED),
        (
            "CREATE UNIQUE INDEX CONCURRENTLY idx ON table_name (column_name);",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "CREATE UNIQUE INDEX idx ON table_name (column_name);",
            StatementType.RESTRICTED,
        ),
        ("DROP INDEX idx;", StatementType.RESTRICTED),
        ("DROP INDEX CONCURRENTLY idx;", StatementType.BACKWARD_COMPATIBLE),
        ("REINDEX INDEX CONCURRENTLY idx", StatementType.BACKWARD_COMPATIBLE),
        ("REINDEX INDEX idx", StatementType.RESTRICTED),
        ("ALTER INDEX idx RENAME TO new_name;", StatementType.BACKWARD_COMPATIBLE),
        ("CREATE SEQUENCE name;", StatementType.BACKWARD_COMPATIBLE),
        ("ALTER SEQUENCE name START 0;", StatementType.BACKWARD_COMPATIBLE),
        ("ALTER TABLE t_name RENAME TO new_name;", StatementType.RESTRICTED),
        (
            "ALTER TABLE t_name ADD COLUMN c_name text NULL;",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ADD COLUMN c_name text NOT NULL;",
            StatementType.RESTRICTED,
        ),
        (
            "ALTER TABLE t_name ADD COLUMN c_name integer NOT NULL DEFAULT 0;",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ADD COLUMN c_name integer NULL DEFAULT 0;",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ADD COLUMN c_name bigserial PRIMARY KEY;",
            StatementType.BACKWARD_INCOMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ADD COLUMN c_name UUID PRIMARY KEY;",
            StatementType.BACKWARD_INCOMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ALTER COLUMN c_name SET NOT NULL;",
            StatementType.BACKWARD_INCOMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ALTER COLUMN c_name DROP NOT NULL;",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ALTER COLUMN c_name SET DEFAULT 0;",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ALTER COLUMN c_name DROP DEFAULT;",
            StatementType.BACKWARD_INCOMPATIBLE,
        ),
        (
            "ALTER TABLE t_name DROP CONSTRAINT c_name;",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ADD CONSTRAINT name FOREIGN KEY (c_name) REFERENCES some_table (id);",
            StatementType.RESTRICTED,
        ),
        (
            "ALTER TABLE t_name ADD CONSTRAINT name FOREIGN KEY (c_name) REFERENCES some_table (id) NOT VALID;",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        ("UPDATE t_name SET col=0", StatementType.DATA_MIGRATION),
        ("DELETE FROM t_name WHERE col=0", StatementType.DATA_MIGRATION),
        (
            "INSERT INTO t_name (id, name) VALUES (1, 'foo')",
            StatementType.DATA_MIGRATION,
        ),
        (
            "ALTER TABLE t_name VALIDATE CONSTRAINT c_name;",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ALTER COLUMN c_name TYPE text;",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ALTER COLUMN c_name TYPE varchar(10);",
            StatementType.RESTRICTED,
        ),
        (
            "ALTER TABLE t_name ADD CONSTRAINT c_name UNIQUE (col);",
            StatementType.RESTRICTED,
        ),
        (
            "ALTER TABLE t_name ADD CONSTRAINT c_name UNIQUE USING INDEX i_name;",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "ALTER TABLE t_name ADD CONSTRAINT c_name PRIMARY KEY USING INDEX i_name",
            StatementType.BACKWARD_INCOMPATIBLE,
        ),
        (
            "ALTER TABLE t_name RENAME COLUMN c_name TO another_name",
            StatementType.BACKWARD_INCOMPATIBLE,
        ),
        (
            """
            CREATE TRIGGER tr_name
            BEFORE INSERT ON t_name
            FOR EACH ROW EXECUTE FUNCTION f_name()
            """,
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "DROP TRIGGER t_name ON tbl_name",
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            """
            CREATE OR REPLACE FUNCTION f_name() RETURNS TRIGGER AS $$
            BEGIN
              NEW."new_id" := NEW."id";
              RETURN NEW;
            END $$ LANGUAGE plpgsql
            """,
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            "DROP FUNCTION t_name",
            StatementType.BACKWARD_COMPATIBLE,
        ),
    ],
)
def test_classify_migration(statement: str, expected_type: StatementType):
    result = classify_migration(statement)
    assert len(result) == 1
    assert result[0][1] == expected_type


def test_ignore_order():
    result = classify_migration(
        "ALTER TABLE t_name ADD COLUMN c_name integer NOT NULL DEFAULT 0;"
    )
    assert len(result) == 1
    assert result[0][1] == StatementType.BACKWARD_COMPATIBLE

    result = classify_migration(
        "ALTER TABLE t_name ADD COLUMN c_name integer DEFAULT 0 NOT NULL;"
    )
    assert len(result) == 1
    assert result[0][1] == StatementType.BACKWARD_COMPATIBLE

    result = classify_migration(
        "ALTER TABLE t_name ADD COLUMN c_name integer NOT NULL;"
    )
    assert len(result) == 1
    assert result[0][1] == StatementType.RESTRICTED


@pytest.mark.parametrize(
    "sql,expected_type",
    [
        (
            """
            CREATE TABLE t_name (id serial, c_name integer);
            ALTER TABLE t_name ADD CONSTRAINT c_name CHECK (col > 0);
            """,
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            """
            CREATE TABLE t_name (id serial, c_name integer);
            ALTER TABLE another_table ADD CONSTRAINT c_name CHECK (col > 0);
            """,
            StatementType.RESTRICTED,
        ),
        (
            """
            CREATE TABLE t_name (id serial, c_name integer);
            ALTER TABLE t_name ADD FOREIGN KEY (c_name) REFERENCES some_table (id);
            """,
            StatementType.BACKWARD_COMPATIBLE,
        ),
        (
            """
            ALTER TABLE t_name VALIDATE CONSTRAINT c_name;
            ALTER TABLE t_name ALTER COLUMN col SET NOT NULL;
            """,
            StatementType.BACKWARD_COMPATIBLE,
        ),
    ],
)
def test_conditionally_safe(sql: str, expected_type: StatementType):
    result = classify_migration(sql)
    assert len(result) == 2
    # check the last statement type
    assert result[-1][1] == expected_type


@pytest.mark.parametrize(
    "statement,expected_count",
    [
        ("SET statement_timeout=5;", 0),
        ("SET statement_timeout=5; DROP INDEX idx;", 1),
        ("BEGIN; ALTER TABLE t_name ADD COLUMN c_name text NULL; COMMIT;", 1),
    ],
)
def test_ignore_statements(statement: str, expected_count: int):
    statement_types = classify_migration(statement)
    assert len(statement_types) == expected_count
