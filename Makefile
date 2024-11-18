.EXPORT_ALL_VARIABLES:

COMPOSE_FILE ?= docker/docker-compose-local.yml
COMPOSE_PROJECT_NAME ?= migration-lint

DOTENV_BASE_FILE ?= .env-local
DOTENV_CUSTOM_FILE ?= .env-custom

POETRY_EXPORT_OUTPUT = requirements.txt
POETRY_EXTRAS = --extras "git" --extras "django"
POETRY_GROUPS = --with "dev,test"
POETRY_PREINSTALLED ?= false
POETRY_PUBLISH_PRERELEASE ?= false
POETRY_VERSION = 1.2.2
POETRY ?= $(HOME)/.local/bin/poetry

PYTHON_INSTALL_PACKAGES_USING ?= poetry
PYTHONPATH := $(PYTHONPATH):$(CURDIR)/proto/

WHEELHOUSE_HOME ?= .wheelhouse

-include $(DOTENV_BASE_FILE)
-include $(DOTENV_CUSTOM_FILE)

.PHONY: install-poetry
install-poetry:
ifeq ($(POETRY_PREINSTALLED), true)
	$(POETRY) self update $(POETRY_VERSION)
else
	curl -sSL https://install.python-poetry.org | python -
endif

.PHONY: install-packages
install-packages:
ifeq ($(PYTHON_INSTALL_PACKAGES_USING), poetry)
	$(POETRY) install -vv $(POETRY_EXTRAS) $(POETRY_GROUPS) $(opts)
else
	$(POETRY) run pip install \
		--no-index \
		--find-links=$(WHEELHOUSE_HOME) \
		--requirement=$(POETRY_EXPORT_OUTPUT)
endif

.PHONY: install
install: install-poetry install-packages

.PHONY: export-packages
export-packages:
	$(POETRY) export \
		$(POETRY_EXTRAS) \
		$(POETRY_GROUPS) \
		--without-hashes \
		--without-urls \
		--output=$(POETRY_EXPORT_OUTPUT)

.PHONY: prepare-wheels
prepare-wheels: lock-packages export-packages
	@$(POETRY) run pip wheel \
		--wheel-dir=$(WHEELHOUSE_HOME) \
		--find-links=$(WHEELHOUSE_HOME) \
		--requirement=$(POETRY_EXPORT_OUTPUT)

.PHONY: lock-packages
lock-packages:
	$(POETRY) lock -vv --no-update

.PHONY: update-packages
update-packages:
	$(POETRY) update -vv

.PHONY: lint-mypy
lint-mypy:
	$(POETRY) run mypy migration_lint

.PHONY: lint-ruff
ifdef CI
lint-ruff: export RUFF_NO_CACHE=true
endif
lint-ruff:
	$(POETRY) run ruff check .
	$(POETRY) run ruff format --check --diff .

.PHONY: lint-python
lint-python: lint-mypy lint-ruff

.PHONY: lint-markdown
lint-markdown:
	docker run \
		--rm \
		--interactive \
		--read-only \
		--volume=`pwd`:`pwd` \
		--workdir=`pwd` \
		--entrypoint='' \
		registry.gitlab.com/pipeline-components/markdownlint:0.11.3 \
		mdl --style style.rb .

.PHONY: lint
lint: lint-python lint-markdown

.PHONY: fmt-ruff
fmt-ruff:
	$(POETRY) run ruff check . --fix
	$(POETRY) run ruff format .

.PHONY: fmt
fmt: fmt-ruff

.PHONY: test
test:
	$(POETRY) run pytest --cov=migration_lint $(opts) $(call tests,.)

.PHONY: docker-up
docker-up:
	docker compose up --remove-orphans -d
	docker compose ps

.PHONY: docker-down
docker-down:
	docker compose down

.PHONY: docker-logs
docker-logs:
	docker compose logs --follow

.PHONY: docker-ps
docker-ps:
	docker compose ps

.PHONY: publish
publish:
	$(POETRY) publish \
		--no-interaction \
		--build

#.PHONY: release
#release:
#	scripts/release.sh
