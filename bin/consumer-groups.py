#!/usr/bin/env python3

import logging
from telemetry.telescope_msk.cli import cli
from telemetry.telescope_msk.logger import create_app_logger
from telemetry.telescope_msk.consumer import list_offsets, get_consumer
from telemetry.telescope_msk.msk import get_plaintext_bootstrap_servers
from telemetry.telescope_msk.publisher import publish_metric_sums, publish_metrics

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

    consumer = get_consumer(bootstrap_servers, 'telescope-msk')
    metrics = list_offsets(consumer)
    consumer.close()

    publish_metrics(metrics, graphite_host)
    publish_metric_sums(metrics, graphite_host)


if __name__ == '__main__':
    cli(main)
