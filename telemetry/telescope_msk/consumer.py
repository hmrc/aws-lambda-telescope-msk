import confluent_kafka
from confluent_kafka import Consumer, TopicPartition
from confluent_kafka.admin import TopicMetadata
from telemetry.telescope_msk.logger import get_app_logger
# autodetect the environment: local vs AWS
#   if local: tunnel + bootstrap_servers = 'localhost:9092'
#   else: use bootstrap_servers from boto (get_default_bootstrap_servers())

# autodetect topics, exclude "__*" (internal topics)
# for_each topic -> get partitions -> get consumer metrics (consumer offset, lag)
# print on screen
# push this ^ to graphite
# add https://pypi.org/project/graphyte/ or make sure its installed where this runs


def get_consumer(bootstrap_servers: str, group_id: str) -> Consumer:
    return Consumer({
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
    })


# takes a dict of key = group_name, value = topic_name
def get_metrics_for_groups_and_topics(consumer_groups_topic_names: dict) -> list:
    metrics = []
    for group_name in consumer_groups_topic_names:
        topic_name = consumer_groups_topic_names[group_name]
        metrics += get_metrics_for_group_and_topic(group_name, topic_name)


def get_metrics_for_group_and_topic(bootstrap_servers: str, group_name: str, topic_name:str) -> list:
    msk_consumer = get_consumer(bootstrap_servers, group_name)
    metrics = get_metrics_for_topic(msk_consumer, topic_name)
    msk_consumer.close()
    return metrics


def get_metrics_for_topic(consumer: Consumer, topic_name: str) -> list:
    # get topic metadata for topic name
    metadata = consumer.list_topics(topic=topic_name, timeout=10)
    committed_partitions = consumer.committed(get_partitions_for_topics(metadata),timeout=10)
    metrics = get_metrics_for_partitions(consumer, committed_partitions)
    return metrics


# metadata is the ClusterMetadata object returned by consumer.list_topics
def get_partitions_for_topics(metadata: confluent_kafka.admin.ClusterMetadata) -> list:
    partitions = []
    for topic_name in metadata.topics:
        topic = metadata.topics[topic_name]
        partitions += get_partitions_for_topic(topic)
    return partitions


def get_partitions_for_topic(topic: TopicMetadata) -> list:
    logger = get_app_logger()
    print(type(topic.error))
    if topic.error is not None:
        logger.error(topic.error)
        return []

    name = topic.topic
    # Construct TopicPartition list of partitions to query
    return [TopicPartition(name, partition) for partition in topic.partitions]


def get_metrics_for_partitions(consumer, partitions: list) -> list:
    return [get_metrics_for_partition(consumer, partition) for partition in partitions]


def get_metrics_for_partition(consumer: Consumer, partition: TopicPartition) -> dict:
    timeout = 5
    watermarks = consumer.get_watermark_offsets(partition, timeout=timeout, cached=False)
    if watermarks is None:
        raise Exception(f'Getting watermarks for partition:{partition.partition} on topic: {partition.topic} has taken longer than timeout {timeout} seconds')

    (low, high) = watermarks
    # possible negative values for partition offset or high are defined by the following consts
    # confluent_kafka.OFFSET_BEGINNING == -2
    # confluent_kafka.OFFSET_END == -1
    # confluent_kafka.OFFSET_STORED == -1000
    # confluent_kafka.OFFSET_INVALID == -1001
    if high < 0:
        lag = 0  # Unlikely
    elif partition.offset < 0:
        # No committed offset, show total message count as lag.
        # The actual message count may be lower due to compaction
        # and record deletions.
        lag = high - low
    else:
        lag = high - partition.offset
    return {
            "topic_name": partition.topic,
            "partition_id": partition.partition,
            "high": high,
            "low": low,
            "lag": lag,
            "offset": partition.offset
    }