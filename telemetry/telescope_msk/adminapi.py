from confluent_kafka.admin import AdminClient
from telemetry.telescope_msk.logger import get_app_logger

# what do we hope to achieve?
# Grab consumer lag for all consumer groups in a grafana dashboard
#   return a list of consumer groups excluding aws msk
#   transform into a string
#   push to graphite
#   build a grafana dashboard to display it.
#   make available to consumer.py
#   make it run continuously in a ecs task

logger = get_app_logger()


def create_admin_client(bootstrap_servers):
    return AdminClient({'bootstrap.servers': bootstrap_servers})


def list_consumer_groups(admin_client: AdminClient) -> list:
    groups = admin_client.list_groups(timeout=10)
    groups_list = []
    for g in groups:
        if g.error is None:
            groups_list.append(g)
        else:
            logger.error(g.error)
    return groups_list


def list_consumer_groups_excluding(admin_client: AdminClient, exclude_groups: list):
    return [g for g in list_consumer_groups(admin_client) if g.id not in exclude_groups]
