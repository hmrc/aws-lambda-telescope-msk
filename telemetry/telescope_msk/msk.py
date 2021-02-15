# Useful developer docs:
#  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kafka.html#Kafka.Client.list_clusters

import boto3
from telemetry.telescope_msk.logger import get_app_logger
from telemetry.telescope_msk.cli import print_markdown, get_console
from typing import List
from botocore.config import Config

my_config = Config(
    region_name='eu-west-2'
)

DEFAULT_CLUSTER_NAME = 'msk-cluster'

msk_client = boto3.client('kafka', config=my_config)
logger = get_app_logger()


class MskClusterNotFoundException(Exception):
    pass


class MskCluster:
    def __init__(self, info: dict):
        self.info = info

    @property
    def arn(self):
        return self.info['ClusterArn']

    @property
    def creation_time(self):
        return self.info['CreationTime']

    @property
    def kafka_version(self):
        return self.info['CurrentBrokerSoftwareInfo']['KafkaVersion']

    @property
    def status(self):
        return self.info['State']


class BootstrapServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port


class BootstrapServers:
    def __init__(self, plaintext, tls):
        self._plaintext_str = plaintext
        self._plaintext = self._to_list(plaintext)
        self._tls_str = tls
        self._tls = self._to_list(tls)

    @property
    def plaintext(self) -> List[BootstrapServer]:
        return self._plaintext

    @property
    def plaintext_str(self) -> str:
        return self._plaintext_str

    @property
    def tls(self) -> List[BootstrapServer]:
        return self.tls

    @property
    def tls_str(self):
        return self._plaintext_str

    def _to_list(self, connection_string: str) -> List[BootstrapServer]:
        bootstrap_servers = []
        for host_and_port in connection_string.split(","):
            components = host_and_port.split(":")
            bootstrap_servers.append(BootstrapServer(components[0], int(components[1])))

        return bootstrap_servers


def get_cluster_arn(cluster_name: str) -> str:
    logger.debug("Getting the cluster ARN for '%s'" % cluster_name)
    response = msk_client.list_clusters(ClusterNameFilter=cluster_name, MaxResults=1)
    try:
        cluster_arn = response['ClusterInfoList'][0]['ClusterArn']
        logger.debug("MSK cluster ARN: %s" % cluster_arn)

        return cluster_arn
    except IndexError:
        raise MskClusterNotFoundException


def get_cluster_info(cluster_arn: str) -> MskCluster:
    response = msk_client.describe_cluster(
        ClusterArn=cluster_arn
    )

    return MskCluster(response['ClusterInfo'])


def get_bootstrap_servers(cluster_arn: str) -> BootstrapServers:
    """Returns a list of host/port pairs for establishing the initial connection to the Kafka cluster. Use this property
     in your Kafka producer or consumer configuration.
    """
    logger.debug("Fetching bootstrap servers for '%s'" % cluster_arn)
    response = msk_client.get_bootstrap_brokers(
        ClusterArn=cluster_arn
    )

    return BootstrapServers(
        plaintext=response['BootstrapBrokerString'],
        tls=response['BootstrapBrokerStringTls']
    )


def get_default_bootstrap_servers() -> BootstrapServers:
    cluster_arn = get_cluster_arn(DEFAULT_CLUSTER_NAME)
    return get_bootstrap_servers(cluster_arn)


def get_plaintext_bootstrap_servers():
    bootstrap_servers = get_default_bootstrap_servers().plaintext_str
    return bootstrap_servers


def print_summary():
    console = get_console()
    with console.status("[bold green]Fetching cluster info...") as status:
        cluster_arn = get_cluster_arn(DEFAULT_CLUSTER_NAME)
        msk_cluster = get_cluster_info(cluster_arn)
        bootstrap_servers = get_bootstrap_servers(cluster_arn)

    console.print(f"[b u]{DEFAULT_CLUSTER_NAME}[/b u]")

    # Cluster Summary
    console.print(f"\n[cyan]Cluster summary[/cyan]\n")
    console.print(f"  Status: [yellow]{msk_cluster.status}[/yellow]")
    console.print(f"  Kafka version: [yellow]{msk_cluster.kafka_version}[/yellow]")
    console.print(f"  Creation Time: [yellow]{msk_cluster.creation_time}[/yellow]")
    console.print(f"  ARN: [yellow]{msk_cluster.arn}[/yellow]")

    # Client Information
    console.print(f"\n[cyan]Bootstrap servers[/cyan]\n")
    console.print(f"  TLS: [yellow]{bootstrap_servers.tls_str}[/yellow]")
    console.print(f"  Plaintext: [yellow]{bootstrap_servers.plaintext_str}[/yellow]")

