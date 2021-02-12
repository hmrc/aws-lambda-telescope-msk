#!/usr/bin/env python3

import logging
from telemetry.telescope_msk.cli import cli
from telemetry.telescope_msk.logger import create_app_logger
from telemetry.telescope_msk.consumer import list_offsets


def main(local: bool = False, log_level: str = logging.DEBUG) -> None:
    create_app_logger(log_level)
    list_offsets(local)


if __name__ == '__main__':
    cli(main)