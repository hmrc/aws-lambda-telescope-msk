from telescope_msk.logger import get_app_logger
import socket
from contextlib import closing


def ping_brokers(hostnames: str):
    for server in hostnames.split(","):
        ping_broker(server)


def ping_broker(hostname: str):
    logger = get_app_logger()
    url, port = hostname.split(":")
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.settimeout(5)
        logger.debug(f"pinging: {hostname}")
        try:
            s.connect((url, int(port)))
        except Exception as e:
            logger.error(f"Error connecting to broker at: {hostname}: {e}")
        finally:
            s.close()
