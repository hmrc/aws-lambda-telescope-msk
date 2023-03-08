# aws-lambda-telescope-msk

[![Brought to you by Telemetry Team](https://img.shields.io/badge/MDTP-Telemetry-40D9C0?style=flat&labelColor=000000&logo=gov.uk)](https://confluence.tools.tax.service.gov.uk/display/TEL/Telemetry)

Telescope library for interacting with an MSK/Kafka cluster. This lambda is responsible for fetching metrics about MSK and passing them to Clickhouse. An example usage of the metrics can be seen on the Telescope MSK Grafana Dashboard.

## Requirements

* [Python 3.9+](https://www.python.org/downloads/release)
* [Poetry](https://python-poetry.org/)
* [librdkafka](https://github.com/edenhill/librdkafka)

## Quick start

Install dependencies using Poetry:

```shell
make setup
```

All available interactions with the MSK cluster are packaged as individual Python scripts in `bin/`.
Run each script as `poetry run bin/<script.py>` prefixed with the desired AWS profile.
Example:

```shell
aws-profile -p telemetry-mdtp-staging-RoleTelemetryAdministrator poetry run bin/consumer-groups.py --help
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
aws-profile -p telemetry-mdtp-staging-RoleTelemetryAdministrator \
  poetry run bin/consumer-groups.py --help
```

### Sync and run in ECS
### ECS is currently unavailable as of TEL-2300, permissions to run telemetry ecs must be added to the labs security group if wanting to run


```sh
export ECS_INSTANCE_IP_ADDRESS=10.3.0.191
ssh $ECS_INSTANCE_IP_ADDRESS
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
./poetry/bin/poetry install
export AWS_DEFAULT_REGION=eu-west-2
python3 .poetry/bin/poetry run python3 bin/consumer-groups.py
```

## Poetry Install on Mac M1 chips

These instructions are taken from [this source](https://segmentfault.com/a/1190000040867082/en)

* Install librdkafka using Brew
* Set environment variables to point at install location
* Run poetry install/update as appropriate

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
