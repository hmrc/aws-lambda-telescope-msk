# aws-lambda-telescope-msk

[![Brought to you by Telemetry Team](https://img.shields.io/badge/MDTP-Telemetry-40D9C0?style=flat&labelColor=000000&logo=gov.uk)](https://confluence.tools.tax.service.gov.uk/display/TEL/Telemetry)

Telescope library for interacting with an MSK/Kafka cluster. This lambda is responsible for fetching metrics about MSK
and passing them to Clickhouse. An example usage of the metrics can be seen on the Telescope MSK Grafana Dashboard.

## Table of Contents
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Simple Producer Test Lambda](#simple-producer-test-lambda)
- [Local development](#local-development)
- [Package Install on Mac M1 chips](#package-install-on-mac-m1-chips)
- [License](#license)

<!-- END doctoc -->

## Prerequisites

* [mise](https://mise.jdx.dev/) to manage tool versions and integrates with `uv`.
* [uv](https://docs.astral.sh/uv/) to manage Python virtual environments and dependencies.

## Quick start

Install dependencies using uv:

```shell
mise run setup
```

All available interactions with the MSK cluster are packaged as individual Python scripts in `bin/`.
Run each script as `uv run bin/<script.py>` setup with the desired AWS profile.
Example:

```shell
uv run bin/consumer-groups.py --help
```

## Simple Producer Test Lambda
The python script `producer.py` is used as a lambda function's handler entrypoint. This lambda can be used to test
generating messages as a Kafka producer. All it requires is a lambda test payload that defines the target topic and the
data to be posted to the topic. For example:

```json
{
  "topic": "logs",
  "data": {
    "data0": "hello",
    "data1": "world"
  }
}
```

## Local development

To run locally the plaintext bootstrap cluster host names must be added to local host IP address:
```
127.0.0.1       localhost       b-1.msk-cluster.mmfn29.c4.kafka.eu-west-2.amazonaws.com:9092,b-2.msk-cluster.mmfn29.c
4.kafka.eu-west-2.amazonaws.com:9092,b-3.msk-cluster.mmfn29.c4.kafka.eu-west-2.amazonaws.com:9092
```
Fetch the ip from ecs node on aws console,
Then an SSH tunnel must be set up using an the ip to forward the port to localhost:
```sh
ssh -L 9092:localhost:9092 10.3.0.191
```
Once a port is open you can run the standard scripts as above:
```sh
uv run bin/consumer-groups.py --help
```

## Package Install on Mac M1 chips

These instructions are taken from [this source](https://segmentfault.com/a/1190000040867082/en)

* Install librdkafka using Brew
* Set environment variables to point at install location
* Run uv install/update as appropriate

```shell
brew install librdkafka
# Get the version number installed
ls -la /opt/homebrew/Cellar/librdkafka
# Export the file paths
export C_INCLUDE_PATH=/opt/homebrew/Cellar/librdkafka/1.8.2/include
export LIBRARY_PATH=/opt/homebrew/Cellar/librdkafka/1.8.2/lib
```

## License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
