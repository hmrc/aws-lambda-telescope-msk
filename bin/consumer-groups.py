#!/usr/bin/env python3

import logging

from telemetry.telescope_msk.adminapi import list_consumer_groups, create_admin_client, list_consumer_groups_excluding
from telemetry.telescope_msk.cli import cli
from telemetry.telescope_msk.logger import create_app_logger
from telemetry.telescope_msk.consumer import list_offsets, get_consumer
from telemetry.telescope_msk.msk import get_plaintext_bootstrap_servers


# what do we hope to achieve?
# Overall grab consumer lag for all consumer groups in a grafana dashboard
# / Return a list of consumer groups excluding aws msk
# / filter out __consumer_offsets and __aws_msk_etc
# /  Get the metrics for each partition in group
#   Transform into a string  something like ${consumer_group}-${partition}-${topic_name}, Check with Vitor
#   Push to graphite
#   Build a grafana dashboard to display it.
#   Make available to consumer.py
#   Make it run continuously in a ecs task


def main(log_level: str = logging.DEBUG) -> None:
    bootstrap_servers = get_plaintext_bootstrap_servers()
    create_app_logger(log_level)
    consumer_groups = list_consumer_groups_excluding(create_admin_client(bootstrap_servers),
                                                     ['amazon.msk.canary.group.broker-3',
                                                      'amazon.msk.canary.group.broker-2',
                                                      'amazon.msk.canary.group.broker-1'])

    for group in consumer_groups:
        print(f'\n\n{group.id}')
        consumer = get_consumer(bootstrap_servers, group.id)
        print("\n".join(list_offsets(consumer)))
        consumer.close()

        '{consumer_group}.{topic_name}.partition_{partition}-{high/low/lag}'
        #logstash.logs.partition_0.high.$high_watermark

if __name__ == '__main__':
    cli(main)
