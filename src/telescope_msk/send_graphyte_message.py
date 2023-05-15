from telescope_msk.app_info import METRICS_PREFIX
from telescope_msk.graphyte import init
from telescope_msk.graphyte import send
from telescope_msk.logger import get_app_logger


logger = get_app_logger()


def publish_kafka_to_graphite(path, metrics, graphite_host):
    init(graphite_host, prefix=METRICS_PREFIX)
    send(path, metrics)
