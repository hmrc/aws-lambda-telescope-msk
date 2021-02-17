#!/usr/bin/env python3

import logging

from telemetry.telescope_msk.adminapi import list_consumer_groups, create_admin_client
from telemetry.telescope_msk.cli import cli
from telemetry.telescope_msk.logger import create_app_logger
from telemetry.telescope_msk.consumer import list_offsets, get_consumer
from telemetry.telescope_msk.msk import get_plaintext_bootstrap_servers


def main(log_level: str = logging.DEBUG) -> None:
    create_app_logger(log_level)
    # consumer = get_consumer(get_plaintext_bootstrap_servers())
    # list_offsets(consumer)
    # consumer.close()
    print(list_consumer_groups(create_admin_client(get_plaintext_bootstrap_servers())))
    # print(list_consumer_groups_excluding(['amazon.msk.canary.group.broker-3',
    #       'amazon.msk.canary.group.broker-2', 'amazon.msk.canary.group.broker-1']))


if __name__ == '__main__':
    cli(main)
