#!/usr/bin/env python3

import logging
from pprint import pprint

from telemetry.telescope_msk.cli import cli
from telemetry.telescope_msk.logger import create_app_logger
from telemetry.telescope_msk.consumer import get_metrics_for_groups_and_topics
from telemetry.telescope_msk.msk import get_plaintext_bootstrap_servers

# what do we hope to achieve?
# Overall grab consumer lag for all consumer groups in a grafana dashboard
# / Return a list of consumer groups excluding aws msk
# / filter out __consumer_offsets and __aws_msk_etc
# / Get the metrics for each partition in group
# / Transform into a string  something like ${partition}-${topic_name}-${metric_name}, Check with Vitor
# / Push to graphite
# / Build a grafana dashboard to display it.
# / Make available to consumer.py
#   Make it run continuously in a ecs task


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
