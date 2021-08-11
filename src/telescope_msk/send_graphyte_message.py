import graphyte

from src.telescope_msk.app_info import METRICS_PREFIX
from src.telescope_msk.logger import get_app_logger


logger = get_app_logger()


def publish_kafka_to_graphite(path, metrics, graphite_host):
    graphyte.init(graphite_host, prefix=METRICS_PREFIX)
    graphyte.send(path, metrics)
