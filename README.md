# Telescope MSK

Hello, Sam!

Telescope library for interacting with an MSK/Kafka cluster.

## Requirements

* [Python 3.8+](https://www.python.org/downloads/release)
* [Poetry](https://python-poetry.org/)
* [librdkafka](https://github.com/edenhill/librdkafka)

## Quick start

Install dependencies using Poetry:

```sh
poetry install
```

All available interactions with the MSK cluster are packaged as individual Python scripts in `bin/`. 
Run each script as `poetry run bin/<script.py>` prefixed with the desired AWS profile. 
Example:

```sh
aws-profile -p telemetry-mdtp-staging-RoleTelemetryEngineer \
  poetry run bin/consumer-groups.py --help
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
aws-profile -p telemetry-mdtp-staging-RoleTelemetryEngineer \
  poetry run bin/consumer-groups.py --help
```
## License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
