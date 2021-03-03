from telemetry.telescope_msk import get_graphite_host, get_plaintext_bootstrap_servers, get_consumer, list_offsets, \
    publish_metrics, publish_metric_sums
import os
import logging
from telemetry.telescope_msk.logger import create_app_logger, get_app_logger
import socket

def get_graphite_host():
    return os.environ.get("graphite_host", "graphite")


def ping(hostname: str):
    logger = get_app_logger()
    url, port = hostname.split(":")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        if s.create_connection((url, int(port))) == 0:
            logger.debug(f'{hostname} Port is open')
        else:
            logger.error(f'{hostname} Port is not open')
        s.close()
    except Exception as e:
        logger.error(f"error connecting to {hostname}: {e}")


def lambda_handler(event, context):
    print("HELLO WORLD 11111!!!")
    msk_logger = create_app_logger(logging.DEBUG)
    msk_logger.debug("HELLO LOGGER22222!!!!")

    try:
        msk_logger.info(f"Lambda Request ID: {context.aws_request_id}")
    except AttributeError:
        msk_logger.debug(f"No context object available")

    try:
        graphite_host = get_graphite_host()
        bootstrap_servers = get_plaintext_bootstrap_servers()
        msk_logger.debug(bootstrap_servers)


        for server in bootstrap_servers.split(","):
            ping(server)




        msk_consumer = get_consumer(bootstrap_servers, 'telescope-msk')
        msk_logger.debug(f'consumer {msk_consumer}')
        metrics = list_offsets(msk_consumer)
        msk_consumer.close()

        publish_metrics(metrics, graphite_host)
        publish_metric_sums(metrics, graphite_host)
        return {
            'success': True
        }
    except Exception as e:
        msk_logger.error(f"publish msk offsets failed: {e}")

        return {
            'success': False,
            'errorMessage': str(e)
        }