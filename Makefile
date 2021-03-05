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

sync-to-ecs: ## Sync local source files to ECS instance
	@rsync -av bin telemetry 10.3.0.191:~/
.PHONY: sync-to-ecs

SHELL := /usr/bin/env bash
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

TELEMETRY_INTERNAL_BASE_ACCOUNT_ID := 634456480543
BUCKET_NAME := telemetry-lambda-artifacts-internal-base
LAMBDA_NAME := telescope-msk

help: ## The help text you're reading
	@grep --no-filename -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help

package:
	@mkdir -p build/deps
	@poetry export -f requirements.txt --without-hashes -o build/deps/requirements.txt
	@pip3 install --target build/deps -r build/deps/requirements.txt
	@mkdir -p build/artifacts
	# @zip -r build/artifacts/${LAMBDA_NAME}.zip telemetry
	@zip -r build/artifacts/${LAMBDA_NAME}.zip main.py telemetry
	@cd build/deps && zip -r ../artifacts/${LAMBDA_NAME}.zip . && cd -
	@openssl dgst -sha256 -binary build/artifacts/${LAMBDA_NAME}.zip | openssl enc -base64 > build/artifacts/${LAMBDA_NAME}.zip.base64sha256
	file --mime-type build/artifacts/${LAMBDA_NAME}.zip.base64sha256
.PHONY: package

publish:
	@if [ "$$(aws sts get-caller-identity | jq -r .Account)" != "${TELEMETRY_INTERNAL_BASE_ACCOUNT_ID}" ]; then \
  		echo "Please make sure that you execute this target with a \"telemetry-internal-base\" AWS profile. Exiting."; exit 1; fi
	aws s3 cp build/artifacts/${LAMBDA_NAME}.zip s3://${BUCKET_NAME}/build-telescope-msk-lambda/${LAMBDA_NAME}.zip --acl=bucket-owner-full-control
	aws s3 cp build/artifacts/${LAMBDA_NAME}.zip.base64sha256 s3://${BUCKET_NAME}/build-telescope-msk-lambda/${LAMBDA_NAME}.zip.base64sha256 --content-type text/plain --acl=bucket-owner-full-control
.PHONY: publish

test:
	@poetry run pytest --cov=telemetry --full-trace --verbose
.PHONY: test