#!/usr/bin/env python3

import logging
from telemetry.telescope_msk.cli import cli
from telemetry.telescope_msk.logger import create_app_logger
from telemetry.telescope_msk.msk import print_summary


def main(log_level: str = logging.INFO) -> None:
    create_app_logger(log_level)
    print_summary()


if __name__ == '__main__':
    cli(main)