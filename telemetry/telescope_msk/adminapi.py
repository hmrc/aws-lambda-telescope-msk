from confluent_kafka.admin import AdminClient
from telemetry.telescope_msk.logger import get_app_logger

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
