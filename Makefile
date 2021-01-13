SHELL := /usr/bin/env bash
PWD = $(shell pwd)
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

DOCKER_AWS_VARS = -e AWS_REGION=${AWS_REGION} -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}

default: help

help: ## The help text you're reading
	@grep --no-filename -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help

remote-setup: ## Prepare a remote ECS EC2 instance to run telescope-msk
	@curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -o dist/get-poetry.py
	@./remote-setup.sh
.PHONY: remote-setup

docker-build-py36: ## Build the Python 3.6 container
	@docker build -t telemetry/telescope-msk:latest .
.PHONY: docker-build-py36

build: docker-build-py36 ## Install local Poetry dependencies and build the Python 3.6 image
	$(MAKE) poetry-install
	@poetry export -f requirements.txt --without-hashes -o requirements.txt
	$(MAKE) poetry-build
.PHONY: build

poetry-install: ## Downloads and installs all the dependencies outlined in the poetry.lock file
	@SODIUM_INSTALL=system poetry install -vvv
.PHONY: poetry-install

poetry-build: ## Builds a tarball and a wheel Python packages
	@poetry build
.PHONY: poetry-build

poetry-update: ## Update the dependencies as according to the pyproject.toml file
	@poetry update -vvv
.PHONY: poetry-update

rsync:
	@./rsync.sh
.PHONY: rsync
