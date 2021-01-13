# Telescope MSK

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

## License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
