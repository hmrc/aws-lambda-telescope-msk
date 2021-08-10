#!/usr/bin/env python3

import logging
from srctelescope_msk.cli import cli
from srctelescope_msk.logger import create_app_logger
from srctelescope_msk import print_summary


def main(log_level: str = logging.INFO) -> None:
    create_app_logger(log_level)
    print_summary()


if __name__ == '__main__':
    cli(main)