import confluent_kafka
from confluent_kafka import Consumer
from confluent_kafka.cimpl import TopicPartition
from confluent_kafka.admin import TopicMetadata
from telemetry.telescope_msk.logger import get_app_logger
from telemetry.telescope_msk.msk import get_plaintext_bootstrap_servers
from telemetry.telescope_msk.msk import get_bootstrap_servers
from telemetry.telescope_msk import APP_NAME
from telemetry.telescope_msk.msk import get_default_bootstrap_servers

# autodetect the environment: local vs AWS
#   if local: tunnel + bootstrap_servers = 'localhost:9092'
#   else: use bootstrap_servers from boto (get_default_bootstrap_servers())

# autodetect topics, exclude "__*" (internal topics)
# for_each topic -> get partitions -> get consumer metrics (consumer offset, lag)
# print on screen
# push this ^ to graphite
# add https://pypi.org/project/graphyte/ or make sure its installed where this runs

logger = get_app_logger()


def get_consumer(bootstrap_servers: str, group_id: str) -> Consumer:
    return Consumer({
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
    })


def list_topics(consumer: Consumer) -> list:
    metadata = consumer.list_topics(timeout=10)
    # filters out __consumer_offsets and __amazon_msk_canary etc
    return [metadata.topics[topic_name] for topic_name in metadata.topics
            if topic_name in metadata.topics and topic_name[0] != "_"]


def list_offsets(consumer: Consumer):
    offsets = []
    try:
        topics = list_topics(consumer)
        for topic in topics:
            for partition in get_committed_partitions_for_topic(consumer, topic):
                offsets.append(return_metrics_for_partition(consumer, partition))

    except Exception as e:
        logger.error(e)

    return offsets


def get_committed_partitions_for_topic(consumer: Consumer, topic: TopicMetadata) -> list:
    name = topic.topic

    if topic.error is not None:
        logger.error(topic.error)

    # Construct TopicPartition list of partitions to query
    partitions = [confluent_kafka.TopicPartition(name, partition) for partition in topic.partitions]

    # Query committed offsets for this group and the given partitions
    return consumer.committed(partitions, timeout=10)


def return_metrics_for_partition(consumer: Consumer, partition: TopicPartition) -> dict:
    try:
        (lo, hi) = consumer.get_watermark_offsets(partition, timeout=5, cached=False)

        if hi < 0:
            lag = None  # Unlikely
        elif partition.offset < 0:
            # OFFSET_INVALID, OFFSET_STORED, OFFSET_END, and OFFSET_BEGINNING are all numerical consts that are < 0

            # No committed offset, show total message count as lag.
            # The actual message count may be lower due to compaction
            # and record deletions.
            lag = hi - lo
        else:
            lag = hi - partition.offset
        return {
                "topic_name": partition.topic,
                "partition_id": partition.partition,
                "high": hi,
                "low": lo,
                "lag": lag}
    except Exception as e:
        print("exception raised")
        logger.error(e)
