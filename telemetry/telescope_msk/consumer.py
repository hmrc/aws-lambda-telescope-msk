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


def list_topics(consumer: Consumer) -> list:

    metadata = consumer.list_topics(timeout=10)
    # filters out __consumer_offsets and __amazon_msk_canary etc
    return [metadata.topics[topic_name] for topic_name in metadata.topics
            if topic_name in metadata.topics and topic_name[0] != "_"]


def list_offsets(consumer: Consumer) -> list:
    logger = get_app_logger()
    offsets = []
    try:
        topics = list_topics(consumer)
        logger.debug(topics)
        for topic in topics:
            for partition in get_committed_partitions_for_topic(consumer, topic):
                offsets.append(return_metrics_for_partition(consumer, partition))

    except Exception as e:
        logger.error(e)

    logger.debug(offsets)
    return offsets


def list_offsets_for_topic(consumer: Consumer, topic_name: str) -> list:
    metadata = consumer.list_topics(timeout=10)
    topic = metadata.topics.get(topic_name)
    if topic is not None:
        offsets = []
        for partition in get_committed_partitions_for_topic(consumer, topic):
            offsets.append(return_metrics_for_partition(consumer, partition))
        return offsets

    raise Exception(f'Unable to find topic with name: {topic_name}')


def get_partitions_for_topic(topic: TopicMetadata) -> list:
    logger = get_app_logger()
    name = topic.topic

    if topic.error is not None:
        logger.error(topic.error)

    # Construct TopicPartition list of partitions to query
    return [confluent_kafka.TopicPartition(name, partition) for partition in topic.partitions]


def get_committed_partitions_for_topic(consumer: Consumer, topic: TopicPartition) -> list:
    return consumer.committed(get_partitions_for_topic(topic), timeout=10)


def return_metrics_for_partition(consumer: Consumer, partition: confluent_kafka.TopicPartition) -> dict:
    logger = get_app_logger()
    try:
        (low, high) = consumer.get_watermark_offsets(partition, timeout=5, cached=False)
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
    except Exception as e:
        print("exception raised")
        logger.error(e)
