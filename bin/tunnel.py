#!/usr/bin/env python3

import logging

import sshtunnel

from srctelescope_msk.cli import cli
from srctelescope_msk.ec2 import get_ecs_instance_ip_address
from srctelescope_msk.logger import create_app_logger
from srctelescope_msk.msk import get_default_bootstrap_servers


def main(log_level: str = logging.DEBUG) -> None:
    create_app_logger(log_level)
    ecs_instance_ip_address = get_ecs_instance_ip_address()
    bootstrap_server = get_default_bootstrap_servers().plaintext[0]
    print(bootstrap_server.host)
    print(bootstrap_server.port)

    with sshtunnel.open_tunnel(
            (REMOTE_SERVER_IP, bootstrap_server.port),
            ssh_username="",
            ssh_pkey="/var/ssh/rsa_key",
            ssh_private_key_password="secret",
            remote_bind_address=(PRIVATE_SERVER_IP, 22),
            local_bind_address=('0.0.0.0', 10022)
    ) as tunnel:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('127.0.0.1', 10022)
        # do some operations with client session
        client.close()

    print('FINISH!')


if __name__ == '__main__':
    cli(main)