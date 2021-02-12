import confluent_kafka
from confluent_kafka import Consumer
from confluent_kafka.cimpl import TopicPartition

from telemetry.telescope_msk.msk import get_default_bootstrap_servers

# autodetect the environment: local vs AWS
#   if local: tunnel + bootstrap_servers = 'localhost:9092'
#   else: use bootstrap_servers from boto (get_default_bootstrap_servers())

# autodetect topics, exclude "__*" (internal topics)
# for_each topic -> get partitions -> get consumer metrics (consumer offset, lag)
# print on screen
# push this ^ to graphite
# add https://pypi.org/project/graphyte/ or make sure its installed where this runs

# telemetry.msk.topic.logs.partition.0.lag = 123456

def list_offsets(local=False):
    local_bootstrap_servers = 'localhost:9091,localhost:9092,localhost:9093'
    bootstrap_servers = get_default_bootstrap_servers().plaintext_str if not local else local_bootstrap_servers

    consumer = Consumer({
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'logstash',

    })
    topic = 'logs'

    try:
        metadata = consumer.list_topics(topic, timeout=10)
        print(metadata)

        print(metadata.topics)

        if metadata.topics[topic].error is not None:
            raise confluent_kafka.KafkaException(metadata.topics[topic].error)

        # Construct TopicPartition list of partitions to query
        partitions = [confluent_kafka.TopicPartition(topic, p) for p in metadata.topics[topic].partitions]
        print(partitions)

        # Query committed offsets for this group and the given partitions
        committed = consumer.committed(partitions, timeout=10)
        #
        for partition in committed:
            print(f"\nCalling return_metrics_for_partition() for {partition}")
            metrics = return_metrics_for_partition(consumer, partition)
            print(metrics)

    except Exception as e:
        print(e)
    consumer.close()


def return_metrics_for_partition(consumer: Consumer, partition: TopicPartition) -> dict:
    try:
        (lo, hi) = consumer.get_watermark_offsets(partition, timeout=5, cached=False)

        # if partition.offset == confluent_kafka.OFFSET_INVALID:
        #     offset = "-"
        # else:
        #     offset = "%d" % (partition.offset)

        if hi < 0:
            lag = None  # Unlikely
        elif partition.offset < 0:
            # No committed offset, show total message count as lag.
            # The actual message count may be lower due to compaction
            # and record deletions.
            lag = hi - lo
        else:
            lag = hi - partition.offset

        return {"High": hi,
                   "Low": lo,
                   "Lag": lag}
    except Exception as e:
        print(e)