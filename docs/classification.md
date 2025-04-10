# DB migrations classification

## Context

This DB migration classification is intended to be
a basis for the unified DB migrations process.

### Migrations Classification

### Common Multi-Stage Migrations Pattern

All stages are optional.

| Name   | Description                                                      | Autorun?       |
|--------|------------------------------------------------------------------|----------------|
| stage1 | Backward-compatible schema migration + (optional) code migration | safe          |
| stage2 | Backfilling data migration                                       | * not safe on prod, safe on stagings |
| stage3 | Code update that is a preparation for backward-incompatible schema migration | |
| stage4 | Backward-incompatible schema migration                           | * no on prod  |

According to this pattern, we distinguish the following types of migrations:

| Name                                    | Stages               |
|-----------------------------------------|-----------------------|
| Data migration                          | * stage2             |
| Backward-compatible migration           | * stage1             |
| Backward-incompatible migration         | * stage3, stage4     |
| Backward-incompatible migration requiring data backfilling | * stage1, stage2, stage3 (optional), stage4 |

### Consequences

* Backward-compatible schema changes can be combined with the corresponding code
  updates (including the code required for backfilling data migrations).
* Code updates required to prepare for backward-incompatible changes
  must be a separate deployment.
* Backward-incompatible schema changes must be a separate deployment.

### Locks

| Name                  | Allowed DQL/DMS Commands | Conflicting DQL/DML Commands |
|-----------------------|-------------------------|------------------------------|
| AccessExclusiveLock   |                         | SELECT, INSERT, UPDATE, DELETE |
| ShareRowExclusiveLock | SELECT                  | INSERT, UPDATE, DELETE       |

### Migrations

### Notes

* We try to make all migrations idempotent.
* We note locks if they are important.

## Index Operations

### Create Index

Backward-compatible migration

* **stage1**
  *`CREATE INDEX CONCURRENTLY IF NOT EXISTS ....`
  *`REINDEX INDEX CONCURRENTLY <index_name>` (if not valid)
  *Update code to use the new index (optional, if the index is used in code).

### Drop Index

Backward-incompatible migration

* **stage3**: Update code to not use an index that will be deleted (optional,
  if the index is used in code).
* **stage4**: `DROP INDEX CONCURRENTLY IF EXISTS <indexname>`.

> **Note**: `DROP INDEX CONCURRENTLY` cannot be used to drop any index
> that supports a constraint. See Drop primary key and Drop UNIQUE constraint.

### Rename Index

Backward-compatible migration

* **stage1**: `ALTER INDEX IF EXISTS ... RENAME TO ....`

### Reindex

Backward-compatible migration

* **stage1**: `REINDEX INDEX CONCURRENTLY ....`

---

## Sequence Operations

### Create Sequence

Backward-compatible migration

* **stage1**:
  * `CREATE SEQUENCE <seqname> ....`
  * Update code to use the new sequence
  (optional, if the sequence is used in code).

### Drop Sequence

Backward-incompatible migration

* **stage3**: Update code to not use a sequence that will be deleted
  (optional, if the sequence is used in code).
* **stage4**: `DROP SEQUENCE <seqname>`.

### Alter Sequence

Backward-compatible migration

* **stage1**: `ALTER SEQUENCE <seqname> ....`

---

## Table Operations

### Create Table

Backward-compatible migration

* **stage1**:
  * `CREATE TABLE <tablename> ...`
  * Update code to use the new table.

> **WARNING**: If there are foreign keys, table creation requires
> `ShareRowExclusiveLock` on the child tables, so use `lock_timeout`
> if the table to create contains foreign keys. `ADD FOREIGN KEY ... NOT VALID`
> does require the same lock, so it doesn’t make much sense
> to create foreign keys separately.

### Drop Table

Backward-incompatible migration

* **stage3**: Update code to not use a table that will be deleted.
* **stage4**:
  * Drop all foreign key constraints to the table (see Drop foreign key).
  * `DROP TABLE <tablename>`.

### Rename Table

Backward-incompatible migration

* **stage1**
  * Rename a table and create a view for backward compatibility
    (`AccessExclusiveLock`).
  * Update code to use the new table name.

```sql
BEGIN;
ALTER TABLE <tablename> RENAME TO <new_tablename>;
CREATE VIEW <tablename> AS
  SELECT * FROM <new_tablename>;
COMMIT;
```

* **stage4**: `DROP VIEW <tablename>`

## Column Operations

### ADD COLUMN ... NULL

Backward-compatible migration

* **stage1**
  * `ALTER TABLE <tablename> ADD COLUMN <colname> ... NULL`
  * Update code to use the new column.

### ADD COLUMN ... NOT NULL

Backward-incompatible migration requiring data backfilling

* **stage1**
  * `ALTER TABLE <tablename> ADD COLUMN <colname> ... DEFAULT <value>`
    (safe from PostgreSQL 11)
  * Update code to use the new column (the code shouldn’t create null values
    for this column)
* **stage2**: Backfill the new column with the default value.
  For existing table with data in it default value is mandatory.
* **stage4**: Add NOT NULL constraint:
  * `ALTER TABLE <tablename> ADD CONSTRAINT <cname>
    CHECK (<colname> IS NOT NULL) NOT VALID`.
  * `ALTER TABLE <tablename> VALIDATE CONSTRAINT <cname>`.
  * `ALTER TABLE <tablename> ALTER COLUMN <colname> SET NOT NULL`
  *(from PostgreSQL 12, “if a valid CHECK constraint is found which proves
  no NULL can exist, then the table scan is skipped”).*
  * `ALTER TABLE <tablename> ALTER COLUMN <colname> DROP DEFAULT`.
  * `ALTER TABLE <tablename> DROP CONSTRAINT IF EXISTS <cname>`.

### ALTER COLUMN ... SET NOT NULL

Backward-incompatible migration requiring data backfilling

* **stage1:**
  * `ALTER TABLE <tablename> ALTER COLUMN <colname>
    SET DEFAULT <default_value>.`
  * Update code to not write null values for the column.
* **stage2**: Backfill the column with the default value.
* **stage4**: Add NOT NULL constraint:
  * `ALTER TABLE <tablename> ADD CONSTRAINT <cname>
    CHECK (<colname> IS NOT NULL) NOT VALID.`
  * `ALTER TABLE <tablename> VALIDATE CONSTRAINT <cname>.`
  * `ALTER TABLE <tablename> ALTER COLUMN <colname> SET NOT NULL`
    *(from PostgreSQL 12, “if a valid CHECK constraint is found
  which proves no NULL can exist, then the table scan is skipped”).*
  * `ALTER TABLE <tablename> ALTER COLUMN <colname> DROP DEFAULT.`
  * `ALTER TABLE <tablename> DROP CONSTRAINT IF EXISTS <cname>.`

### ALTER COLUMN ... DROP NOT NULL

Backward-compatible migration

* **stage1**: `ALTER TABLE <tablename> ALTER COLUMN <colname> DROP NOT NULL.`

### ADD COLUMN ... NULL DEFAULT <value>

Backward-compatible migration (safe from PostgreSQL 11)

* **stage1:**
  * `ALTER TABLE <tablename> ADD COLUMN <colname> ... NULL DEFAULT <value>.`
  * Update code to use the new column.

### ADD COLUMN ... NOT NULL DEFAULT <value>

Backward-compatible migration (safe from PostgreSQL 11)

* **stage1:**
  * `ALTER TABLE <tablename> ADD COLUMN <colname> ... NOT NULL DEFAULT <value>`
  * Update code to use the new column.

### ALTER COLUMN ... SET DEFAULT

Backward-compatible migration

* **stage1**: `ALTER TABLE <tablename> ALTER COLUMN <colname>
  SET DEFAULT <default_value>.`

### ALTER COLUMN ... DROP DEFAULT

Backward-incompatible migration (in the worst case if the column is NOT NULL)

* **stage3**: Update the code to provide the default value
  (optional, if the column is NOT NULL).
* **stage4**: `ALTER TABLE <tablename> ALTER COLUMN <colname> DROP DEFAULT.`

### ADD COLUMN ... bigserial PRIMARY KEY

This is specific case for migrating tables ids from usual int to bigint.

Backward-incompatible migration requiring data backfilling

* **stage1:**
  * `CREATE SEQUENCE <tablename>_<colname>_seq AS bigint START <value>`
  (start value must be greater than number of rows in the table).
  * `ALTER TABLE <tablename> ADD COLUMN <colname> bigint DEFAULT 0,
    ALTER COLUMN <colname> SET DEFAULT nextval('<tablename>_<colname>_seq').`
  * `ALTER SEQUENCE <tablename>_<colname>_seq OWNED BY <tablename>.<colname>.`
* **stage2**: Backfill the new column with values 1 .. N.
* **stage3**: Update the code to use the new column.
* **stage4**: Add a primary key constraint:
  * `ALTER TABLE <tablename> ADD CONSTRAINT <cname>
    CHECK (<colname> IS NOT NULL) NOT VALID.`
  * `ALTER TABLE <tablename> VALIDATE CONSTRAINT <cname>.`
  * `ALTER TABLE <tablename> ALTER COLUMN <colname> SET NOT NULL`
    *(from PostgreSQL 12, “if a valid CHECK constraint is found
  which proves no NULL can exist, then the table scan is skipped”).*
  * `CREATE UNIQUE INDEX CONCURRENTLY <iname> ON <tablename> ....`
  * `ALTER TABLE <tablename> ADD CONSTRAINT <tablename>_pkey PRIMARY KEY
    USING INDEX <iname>.`
  * `ALTER TABLE <tablename> DROP CONSTRAINT IF EXISTS <cname>.`

### ADD COLUMN ... UUID PRIMARY KEY

Backward-incompatible migration requiring data backfilling

* **stage1:**
  * `ALTER TABLE <tablename> ADD COLUMN <colname> UUID.`
  * `ALTER TABLE <tablename> ALTER COLUMN <colname>
    SET DEFAULT gen_random_uuid()`
    *(for PostgreSQL < 13, use uuid_generate_v4 function
  from uuid-ossp extension).*
  * Update the code to use the new field.
* **stage2**: Backfill the new column with unique UUID values.
* **stage4**: Add primary key constraint:
  * `ALTER TABLE <tablename> ADD CONSTRAINT <cname>
    CHECK (<colname> IS NOT NULL) NOT VALID.`
  * `ALTER TABLE <tablename> VALIDATE CONSTRAINT <cname>.`
  * `ALTER TABLE <tablename> ALTER COLUMN <colname> SET NOT NULL`
    *(from PostgreSQL 12, “if a valid CHECK constraint is found
  which proves no NULL can exist, then the table scan is skipped”).*
  * `CREATE UNIQUE INDEX CONCURRENTLY <iname> ON <tablename> ....`
  * `ALTER TABLE <tablename> ADD CONSTRAINT <tablename>_pkey
    PRIMARY KEY USING INDEX <iname>.`
  * `ALTER TABLE <tablename> ALTER COLUMN <colname> DROP DEFAULT.`
  * `ALTER TABLE <tablename> DROP CONSTRAINT IF EXISTS <cname>.`

### ADD COLUMN ... UNIQUE

Backward-compatible migration

* **stage1:**
  * `ALTER TABLE <tablename> ADD COLUMN <colname> ....`
  * `CREATE UNIQUE INDEX CONCURRENTLY <iname> ON <tablename> ....`
  * `ALTER TABLE <tablename> ADD CONSTRAINT <cname> UNIQUE USING INDEX <iname>.`

### ADD COLUMN ... GENERATED AS IDENTITY

This operation going to acquire AccessExclusiveLock and rewrite the whole table
on the spot. So the only safe way to do it is
backward-incompatible migration requiring data backfilling.

* **stage1:**
  * `CREATE SEQUENCE <tablename>_<colname>_seq AS bigint START <value>`
    * Note that start value shouldn't be 1, you need a space to backfill ids.
  * `ALTER TABLE <tablename> ADD COLUMN <colname> bigint DEFAULT 0,
    ALTER COLUMN <colname> SET DEFAULT nextval('<tablename>_<colname>_seq').`
  * `ALTER SEQUENCE <tablename>_<colname>_seq OWNED BY <tablename>.<colname>.`
* **stage2**: Backfill the new column with unique sequential values.
* **stage3**:
  * `ALTER TABLE <tablename> ADD CONSTRAINT <cname>
    CHECK (<colname> IS NOT NULL) NOT VALID`
  * `ALTER TABLE <tablename> VALIDATE CONSTRAINT <cname>`
  * `ALTER TABLE <tablename> ALTER COLUMN <colname> SET NOT NULL`
  * `BEGIN`
  * `ALTER TABLE <tablename> ALTER COLUMN <colname> DROP DEFAULT`
  * `ALTER TABLE <tablename> ALTER COLUMN <colname> ADD GENERATED BY DEFAULT
    AS IDENTITY (START <max_value>)`
  * `COMMIT`
  * `DROP SEQUENCE <tablename>_<colname>_seq`

Be aware that IDENTITY doesn't guarantee that column is unique,
if you want this, take a look on the "Add UNIQUE Constraint" section.

---

### Change Column Type

**Here we have two cases:**

* Backward-compatible migration — directly use `ALTER TABLE <tablename>
  ALTER COLUMN <colname> TYPE ...` and update code in the following cases
  (for PostgreSQL >= 9.2):
  * varchar(LESS) to varchar(MORE) where LESS < MORE
  * varchar(ANY) to text
  * numeric(LESS, SAME) to numeric(MORE, SAME)
  where LESS < MORE and SAME == SAME

Backward-incompatible migration requiring data backfilling in all other cases
  (Tip: It's better to avoid such cases if possible):

* **stage1:**
  * `ALTER TABLE <tablename> ADD COLUMN new_<colname> ...`
  (if column is NOT NULL, add this constraint in a separate migration;
  see ALTER COLUMN ... SET NOT NULL).
  * Dual write to both columns with a BEFORE INSERT/UPDATE trigger:

```sql
CREATE OR REPLACE FUNCTION <fname>()
  RETURNS trigger
AS
$$
BEGIN
  NEW.<new_colname> := NEW.<colname>;
  RETURN NEW;
END
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER <tname>
  BEFORE INSERT OR UPDATE
  ON <tablename>
  FOR EACH ROW
  EXECUTE PROCEDURE <fname>();
```

* **stage2**: Backfill the new column with a copy of the old column’s values.
* **stage4**:
  * Add foreign key constraints referencing the new column
  (see Add foreign key).
  * Drop foreign key constraints referencing the old column
  (see Drop foreign key).
  * Rename <colname> to old_<colname> and new_<colname> to <colname>
  within a single transaction and explicit LOCK <tablename> statement.
  * `DROP TRIGGER <tname>` in the same transaction.
  * `DROP FUNCTION <fname>` in the same transaction.
  * `DROP INDEX CONCURRENTLY` for all indexes using the old column.
  * `DROP COLUMN old_<colname>`.

### Rename Column

**Tip**: Avoid renaming columns when possible.

Backward-incompatible migration requiring data backfilling

* **stage1:**
  * Rename the table and create a view for backward compatibility
  (AccessExclusiveLock).
  * Update code to use the new column.

```sql
BEGIN;

ALTER TABLE <tablename>
  RENAME COLUMN <colname> TO <new_colname>;

ALTER TABLE <tablename> RENAME TO <tablename>_tmp;

CREATE VIEW <tablename> AS
  SELECT *, <new_colname> AS <colname>
  FROM <tablename>_tmp;

COMMIT;
```

* **stage4**: Drop the view and restore the original table name
  (AccessExclusiveLock).

```sql
BEGIN;

DROP VIEW <tablename>;

ALTER TABLE <tablename>_new RENAME TO <tablename>;

COMMIT;
```

**DEPRECATED Approach:**

* **stage1:**
  * `ALTER TABLE <tablename> ADD COLUMN new_<colname> ...`
  (if column is NOT NULL, add this constraint in a separate migration;
  see ALTER COLUMN ... SET NOT NULL).
  * Dual write to both columns with a BEFORE INSERT/UPDATE trigger:

```sql
CREATE OR REPLACE FUNCTION <fname>()
  RETURNS trigger
AS
$$
BEGIN
  NEW.<new_colname> := NEW.<colname>;
  RETURN NEW;
END
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER <tname>
  BEFORE INSERT OR UPDATE
  ON <tablename>
  FOR EACH ROW
  EXECUTE PROCEDURE <fname>();
```

* **stage2**: Backfill the new column with a copy of the old column’s values.
* **stage3**: Update code to use the new column name.
* **stage4**:
  * Add foreign key constraints referencing the new column
  (see Add foreign key).
  * Drop foreign key constraints referencing the old column
  (see Drop foreign key).
  * `DROP TRIGGER <tname>`.
  * `DROP FUNCTION <fname>`.
  * `DROP INDEX CONCURRENTLY` for all indexes using the old column.
  * `DROP COLUMN <colname>`.

### Drop Column

Backward-incompatible migration

* **stage3**: Update code to not use the column that will be dropped.
* **stage4**:
  * Drop foreign key constraints referencing the column (see Drop foreign key).
  * `DROP INDEX CONCURRENTLY` for all indexes using the column.
  * `ALTER TABLE <tablename> DROP COLUMN <colname>`.

## Constraints

### Add NOT NULL Constraint

Backward-compatible migration

* **stage1:**
  * `ALTER TABLE <tablename> ADD CONSTRAINT <cname>
    CHECK (<colname> IS NOT NULL) NOT VALID`.
  * `ALTER TABLE <tablename> VALIDATE CONSTRAINT <cname>`
  (may fail if data is inconsistent).
  * `ALTER TABLE <tablename> ALTER COLUMN <colname> SET NOT NULL`
  (from PostgreSQL 12, “if a valid CHECK constraint is found
  which proves no NULL can exist, then the table scan is skipped”).
  * `ALTER TABLE <tablename> DROP CONSTRAINT IF EXISTS <cname>`.

### Remove NOT NULL Constraint

Backward-compatible migration

* **stage1:** `ALTER TABLE <tablename> ALTER COLUMN <colname> DROP NOT NULL`.

### Add Foreign Key

Backward-compatible migration

* **stage1:**
  * `ALTER TABLE <tablename> ADD FOREIGN KEY ... NOT VALID`.
  * `ALTER TABLE <tablename> VALIDATE CONSTRAINT <cname>`
  (may fail if data is inconsistent).

### Drop Foreign Key

Backward-compatible migration

* **stage1:**
  * `ALTER TABLE <tablename> DROP CONSTRAINT IF EXISTS <cname>`.

### Drop Primary Key Constraint

Backward-compatible migration

* **stage1:**
  * Update code to not rely on the column
  * `DROP INDEX CONCURRENTLY` for all indexes
  * Drop foreign keys in other tables
  * `ALTER TABLE <tablename> DROP CONSTRAINT IF EXISTS <cname>`.

### Add Check Constraints

Backward-compatible migration

* **stage1:**
  * `ALTER TABLE <tablename> ADD CONSTRAINT <cname> CHECK (...) NOT VALID`.
  * `ALTER TABLE <tablename> VALIDATE CONSTRAINT <cname>`.

### Drop Check Constraint

Backward-compatible migration

* **stage1:**
  * `ALTER TABLE <tablename> DROP CONSTRAINT IF EXISTS <cname>`.

### Add UNIQUE Constraint

Backward-compatible migration

* **stage1:**
  * `CREATE UNIQUE INDEX CONCURRENTLY <iname> ON <tablename> ....`
  * `ALTER TABLE <tablename> ADD CONSTRAINT <cname> UNIQUE USING INDEX <iname>`.

### Drop UNIQUE Constraint

Backward-compatible migration

* **stage1:**
  * `DROP INDEX CONCURRENTLY`
  * `SET lock_timeout = '1s';`
  * `ALTER TABLE <tablename> DROP CONSTRAINT IF EXISTS <cname>.`

## Data Migrations

All data migrations operations are lock-safe, but should be done
with batches and considering database load.

## Useful Links

* [tbicr/django-pg-zero-downtime-migrations](https://github.com/tbicr/django-pg-zero-downtime-migrations)
* [PostgreSQL at Scale: Database Schema Changes Without Downtime](https://example.com)
* [Waiting for PostgreSQL 11 – Fast ALTER TABLE ADD COLUMN with a non-NULL default](https://example.com)
