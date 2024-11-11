from typing import Tuple, Sequence, List

from sqlfluff.api.simple import get_simple_config
from sqlfluff.core import Linter
from sqlfluff.dialects.dialect_ansi import StatementSegment

from migration_lint.sql.constants import StatementType
from migration_lint.sql.operations import find_matching_segment
from migration_lint.sql.rules import (
    BACKWARD_INCOMPATIBLE_OPERATIONS,
    BACKWARD_COMPATIBLE_OPERATIONS,
    DATA_MIGRATION_OPERATIONS,
    RESTRICTED_OPERATIONS,
    IGNORED_OPERATIONS,
)


def classify_migration(raw_sql: str) -> Sequence[Tuple[str, StatementType]]:
    """Classify migration statements."""

    linter = Linter(config=get_simple_config(dialect="postgres"))
    result = linter.parse_string(raw_sql)
    parsed = result.root_variant()
    if not parsed or not parsed.tree:
        raise RuntimeError(f"Can't parse SQL from string: {raw_sql}")

    unparsable_parts = [part for part in parsed.tree.recursive_crawl("unparsable")]
    if not parsed or unparsable_parts:
        errors = [
            str(e.description)
            for e in parsed.lexing_violations + parsed.parsing_violations
        ]
        raise RuntimeError(
            f"Can't parse SQL from string: {raw_sql}\n"
            f"Errors: \n" + "\n- ".join(errors)
        )

    statements = []
    statements_types = []
    for statement in parsed.tree.recursive_crawl("statement"):
        statements.append(statement)

    for statement in statements:
        statement_type = classify_statement(statement, context=statements)  # type: ignore
        if statement_type == StatementType.IGNORED:
            continue
        statements_types.append((statement.raw_normalized(), statement_type))

    return statements_types


def classify_statement(
    statement: StatementSegment, context: List[StatementSegment]
) -> StatementType:
    """
    Classify an SQL statement using predefined locators.
    :param statement: statement to classify
    :param context: all statements in the same migration
    :return:
    """

    statement_operations_map = {
        StatementType.IGNORED: IGNORED_OPERATIONS,
        StatementType.DATA_MIGRATION: DATA_MIGRATION_OPERATIONS,
        StatementType.BACKWARD_COMPATIBLE: BACKWARD_COMPATIBLE_OPERATIONS,
        StatementType.BACKWARD_INCOMPATIBLE: BACKWARD_INCOMPATIBLE_OPERATIONS,
        StatementType.RESTRICTED: RESTRICTED_OPERATIONS,
    }

    for statement_type, operations_locators in statement_operations_map.items():
        for locator in operations_locators:
            found_segment = find_matching_segment(
                segment=statement,
                locator=locator,
                context=context,
            )
            if found_segment:
                return statement_type

    return StatementType.UNSUPPORTED
