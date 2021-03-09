import ast
from contextlib import closing

from telemetry.telescope_msk import get_graphite_host, get_plaintext_bootstrap_servers, get_consumer, list_offsets, \
    publish_metrics, publish_metric_sums, list_topic_offsets
import os
import logging

from telemetry.telescope_msk.consumer import list_offsets_for_topic
from telemetry.telescope_msk.logger import create_app_logger, get_app_logger
import socket


def get_graphite_host():
    return os.environ.get("graphite_host", "graphite")


def get_env_bootstrap_servers():
    return os.environ.get("bootstrap_brokers")


def get_consumer_groups_topic_names():
    return ast.literal_eval(os.environ.get("consumer_group_topic_map", "{}"))


def ping(hostname: str):
    logger = get_app_logger()
    url, port = hostname.split(":")
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.settimeout(5)
        logger.debug(f'pinging: {hostname}')
        try:
            s.connect((url, int(port)))
            logger.debug(f'{hostname} Port is open')
        except Exception as e:
            raise Exception(f"error connecting to {hostname}: {e}")
        finally:
            s.close()


def lambda_handler(event, context):
    msk_logger = create_app_logger(logging.DEBUG)
    msk_logger.debug("HELLO WORLD7!!")

    try:
        msk_logger.info(f"Lambda Request ID: {context.aws_request_id}")
    except AttributeError:
        msk_logger.debug(f"No context object available")

    try:
        graphite_host = get_graphite_host()
        bootstrap_servers = get_env_bootstrap_servers()
        # bootstrap_servers = get_plaintext_bootstrap_servers()
        msk_logger.debug(bootstrap_servers)

        for server in bootstrap_servers.split(","):
            ping(server)
    except Exception as e:
        msk_logger.error(f'Cant connect to brokers: {bootstrap_servers}, error:{e}')

    try:

        consumer_groups_topic_names = get_consumer_groups_topic_names()
        for group_id in consumer_groups_topic_names:
            topic_name = consumer_groups_topic_names[group_id]
            msk_consumer = get_consumer(bootstrap_servers, group_id)

            metrics = list_offsets_for_topic(msk_consumer, topic_name)
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