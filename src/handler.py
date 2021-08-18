import ast
import os
import logging
import json

from telescope_msk.broker import ping_brokers
from telescope_msk.consumer import get_metrics_for_groups_and_topics
from telescope_msk.logger import create_app_logger, get_app_logger
from telescope_msk.publisher import publish_metrics, publish_metric_sums

create_app_logger(logging.DEBUG)


def get_graphite_host():
    return os.environ.get("graphite_host", "graphite")


def get_env_bootstrap_servers():
    return os.environ.get("bootstrap_brokers")


def get_consumer_groups_topic_names():
    try:
        env_var = os.environ.get("consumer_group_topic_map", "{}")
        output = json.loads(env_var)
        if type(output) != dict:
            raise Exception("consumer_group_topic_map is not type dict")
    except Exception as e:
        get_app_logger().error(
            f'Unable to get consumer_group to topic name map from env var "consumer_group_topic_map with error: {e}"'
        )

    return output


def lambda_handler(event, context):
    msk_logger = get_app_logger()
    try:
        msk_logger.info(f"Lambda Request ID: {context.aws_request_id}")
    except AttributeError:
        msk_logger.debug(f"No context object available")

    graphite_host = get_graphite_host()
    bootstrap_servers = get_env_bootstrap_servers()

    msk_logger.debug(bootstrap_servers)
    ping_brokers(bootstrap_servers)

    consumer_groups_topic_names = get_consumer_groups_topic_names()
    msk_logger.debug(consumer_groups_topic_names)

    try:
        metrics = get_metrics_for_groups_and_topics(
            bootstrap_servers, consumer_groups_topic_names
        )
        msk_logger.debug(metrics)
        publish_metrics(metrics, graphite_host)
        publish_metric_sums(metrics, graphite_host)

    except Exception as e:
        msk_logger.error(f"Publish msk offsets failed: {e}")
