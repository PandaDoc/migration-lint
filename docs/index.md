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
  for backward incompatible migrations as well as integrated `squawk` linter.

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

## Feedback

We value feedback and are committed to supporting engineers throughout
their journey.

We have a dedicated email where we encourage engineers to share their feedback,
ask questions, and seek assistance with any issues they may encounter.
We appreciate your input and look forward to engaging with you
to make your experience even better.

[:material-email: Write us!](mailto:migration-lint-team@pandadoc.com)
{ .md-button .md-button--primary }
