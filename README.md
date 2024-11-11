# Migration Lint

![ci status](https://github.com/pandadoc/migration-lint/actions/workflows/ci.yml/badge.svg)
![Coverage](https://raw.githubusercontent.com/pandadoc/migration-lint/coverage-badge/coverage.svg)
![Py Version](https://img.shields.io/pypi/pyversions/migration-lint.svg)

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

## Installation

```shell linenums="0"
poetry add "migration-lint"
```

```shell linenums="0"
pip install "migration-lint"
```

## Documentation

Read the docs on [GitHub Pages](https://pandadoc.github.io/migration-lint/)