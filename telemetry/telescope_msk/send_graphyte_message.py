import graphyte
from telemetry.telescope_msk.logger import get_app_logger
from telemetry.telescope_msk import METRICS_PREFIX

logger = get_app_logger()


def publish_asgs_to_graphite(path,metrics, graphite_host):
    logger.info("Publishing msk to graphite")
    send_msk_data(path, metrics, graphite_host)


def send_msk_data(metrics_path, metrics, graphite_host):
    graphyte.init(graphite_host, prefix=METRICS_PREFIX)
    graphyte.send(metrics_path, metrics)
    print(metrics_path,metrics)

