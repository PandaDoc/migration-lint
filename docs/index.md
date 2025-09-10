# Welcome to **migration-lint**

`migration-lint` is the modular linter tool designed
to perform checks on database schema migrations
and prevent unsafe operations.

Features:

- Works with [Django migrations](https://docs.djangoproject.com/en/5.1/topics/migrations/),
  [Alembic](https://alembic.sqlalchemy.org/en/latest/) and raw sql files.
- Easily extensible for other frameworks.
- Can identify Backward Incompatible operations
  and check if they are allowed in the current context.
- Can identify "unsafe" operations, e.g. operations that acquire locks
  that can be dangerous for production database.
- Primary Key Validation: Checks if newly created tables have primary keys
  to ensure better performance and data integrity.

## Installation

```shell linenums="0"
poetry add "migration-lint"
```

```shell linenums="0"
pip install "migration-lint"
```

## Terms

- **Source loader** (or just loader) - class that loads list of changed files.
- **Extractor** - class that extracts SQL by migration name,
  so it depends on the framework you use for migrations.
- **Linter** - class that checks migration's SQL and context
  and returns errors if any. We have implemented our linter
  for backward incompatible migrations, integrated `squawk` linter,
  and added a primary key validation linter.

## Run

### Local

If you need to check local git changes (for example before commit):

```shell linenums="0"
migration-lint --loader=local_git --extractor=<your extractor>
```

It will examine files in current repository that are added or modified
and not yet commited.

### GitLab

If you need to run it on the GitLab pipeline:

```shell linenums="0"
migration-lint --loader=gitlab_branch --extractor=<your extractor>
```

It relies on default GitLab [environment variables](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html),
namely CI_PROJECT_ID, CI_COMMIT_BRANCH.
You also should issue a token with read permissions
and put it into env variable CI_DEPLOY_GITLAB_TOKEN.

Also, these parameters can be passed via options:

```shell linenums="0"
migration-lint --loader=gitlab_branch --extractor=<your extractor>
--project-id=<proj id> --branch=<branch> --gitlab-api-key=<key>
```

Also, version for Merge Requests is available:

```shell linenums="0"
migration-lint --loader=gitlab_branch --extractor=<your extractor>
```

I uses env variable CI_MERGE_REQUEST_ID or option --mr-id.

## Configuration Options

### Primary Key Validation

The primary key linter can be configured using the following option:

```shell
--primary-key-check-dry-run
```

- **Default**: `True` (dry-run mode enabled)
- **Environment variable**: `MIGRATION_LINTER_PRIMARY_KEY_CHECK_DRY_RUN`
- **Description**: When enabled (default), the primary key linter runs in dry-run mode,
  logging warnings about tables created without primary keys but not failing the overall
  linting process. When disabled, missing primary keys are treated as errors.

**Example usage:**

```shell
# Run with primary key validation in dry-run mode (default)
migration-lint --loader=local_git --extractor=django

# Disable dry-run mode to treat missing primary keys as errors
migration-lint --loader=local_git --extractor=django --primary-key-check-dry-run=false
```

## Linters

### Primary Key Linter

The Primary Key Linter checks if newly created tables have primary keys defined.
This is important for database performance and data integrity.

**What it checks:**
- Analyzes `CREATE TABLE` statements in migrations
- Detects tables created without a `PRIMARY KEY` constraint
- Provides helpful warnings or errors depending on configuration

**Example output in dry-run mode:**
```
🔍 Primary Key Check (dry-run mode):
  ⚠️  Table 'user_sessions' created without a primary key:
     CREATE TABLE user_sessions (session_id VARCHAR(255), user_id INTEGER, created_at TIMESTAMP)
  💡 Consider adding a primary key for better performance and data integrity.
```

**Example output when dry-run is disabled:**
```
Errors found in migrations:

- Table 'user_sessions' is created without a primary key: CREATE TABLE user_sessions (session_id VARCHAR(255), user_id INTEGER, created_at TIMESTAMP)
  Consider adding a primary key for better performance and data integrity.
```

**Best practices:**
- Every table should have a primary key for optimal database performance
- Primary keys ensure row uniqueness and enable efficient indexing
- Common primary key patterns include auto-incrementing integers or UUIDs

## Feedback

We value feedback and are committed to supporting engineers throughout
their journey.

We have a dedicated email where we encourage engineers to share their feedback,
ask questions, and seek assistance with any issues they may encounter.
We appreciate your input and look forward to engaging with you
to make your experience even better.

[:material-email: Write us!](mailto:migration-lint-team@pandadoc.com)
{ .md-button .md-button--primary }
