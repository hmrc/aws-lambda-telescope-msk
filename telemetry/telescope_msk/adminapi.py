from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions, ConfigResource, ConfigSource
from telemetry.telescope_msk.msk import get_plaintext_bootstrap_servers
import inspect
from confluent_kafka import KafkaException
import sys
import threading
import logging
from telemetry.telescope_msk.logger import  get_app_logger

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
    # Create Admin client
    return AdminClient({'bootstrap.servers': bootstrap_servers})


def list_consumer_groups():
    a = create_admin_client(get_plaintext_bootstrap_servers())
    groups = a.list_groups(timeout=10)
    print(len(groups))
    return [g if g.error is None else logger.error(g.error) for g in groups]


def list_consumer_groups_excluding(exclude_groups):
    return [g for g in list_consumer_groups() if g.id not in exclude_groups]

