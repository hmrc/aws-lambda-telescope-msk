from telemetry.telescope_msk import get_graphite_host, get_plaintext_bootstrap_servers, get_consumer, list_offsets, \
    publish_metrics, publish_metric_sums
import os
import logging
from telemetry.telescope_msk.logger import create_app_logger


def get_graphite_host():
    return os.environ.get("graphite_host", "graphite")


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