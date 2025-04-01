# Rules API

Linter supports own format for declarative rules definition:

```python

from migration_lint.sql.model import ConditionalMatch, KeywordLocator, SegmentLocator

rule = SegmentLocator(
    type="alter_table_statement",
    children=[
        KeywordLocator(raw="ADD"),
        KeywordLocator(raw="CONSTRAINT"),
        KeywordLocator(raw="NOT", inverted=True),
        KeywordLocator(raw="VALID", inverted=True),
    ],
    only_with=ConditionalMatch(
        locator=SegmentLocator(type="create_table_statement"),
        match_by=SegmentLocator(type="table_reference"),
    ),
)

```

- **SegmentLocator** - definition for any SQL part.
  It can match SQL code segments by a type
  (see [sqlfluff dialects and segment types](https://github.com/sqlfluff/sqlfluff/tree/main/src/sqlfluff/dialects)),
  raw content, children, etc.
- **KeywordLocator** - a short version of SegmentLocator
  if you want to match the exact keyword.
- **inverted=true** - flag for children inverted matching,
  for example in the example above it's
  "find ALTER TABLE ... ADD CONSTRAINT statement, but without NOT VALID".
- **ConditionalMatch** - helps to check the migration context.
  For example, the ADD FOREIGN KEY statement can be highly dangerous
  if you run it on a big table, but if you just created this table,
  it's totally fine. **locator** parameter helps to find statements in the same migration,
  **match_by** helps to match the found statement with the one that is being checked.
  In the example above it's "find in the same migration CREATE TABLE statement
  and ensure that it's the same table".

## Rules order

Rules are being checked from safest to the most dangerous:

- Ignored
- Data migration
- Backward compatible
- Backward incompatible
- Restricted

When you define a backward compatible, make sure that
the rule is as specific as possible so that everything that is not
explicitly allowed would be prohibited.

## Ignoring statements

Add the following line in the migration SQL representation
to ignore whole migration:

```sql
-- migration-lint: ignore
```

If you're using code-based migrations,
make sure that the comment will appear in the SQL:

```python
# example for Alembic
op.execute("SELECT 1; -- migration-lint: ignore")

# example for Django
migrations.RunSQL("SELECT 1; -- migration-lint: ignore", migrations.RunSQL.noop),
```