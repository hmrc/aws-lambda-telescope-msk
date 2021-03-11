#!/usr/bin/env python3

import logging
from pprint import pprint

from telemetry.telescope_msk.cli import cli
from telemetry.telescope_msk.logger import create_app_logger
from telemetry.telescope_msk.consumer import get_metrics_for_groups_and_topics
from telemetry.telescope_msk.msk import get_plaintext_bootstrap_servers



def main(log_level: str = logging.DEBUG, graphite_host="graphite") -> None:
    create_app_logger(log_level)
    bootstrap_servers = get_plaintext_bootstrap_servers()

    consumer_groups_topic_names = {
        'logstash': 'logs',
        'metrics': 'metrics'
    }

    metrics = get_metrics_for_groups_and_topics(bootstrap_servers, consumer_groups_topic_names)
    pprint(metrics)


if __name__ == '__main__':
    cli(main)
