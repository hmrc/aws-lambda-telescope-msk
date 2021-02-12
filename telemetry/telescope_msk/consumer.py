import confluent_kafka
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

def list_offsets():
    # bootstrap_servers = get_default_bootstrap_servers()
    bootstrap_servers = 'localhost:9092'
    from confluent_kafka import Consumer

    consumer = Consumer({
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'metrics',

    })

    topic = 'metrics'

    try:
        metadata = consumer.list_topics(topic, timeout=10)

        # print(metadata.topics)
        if metadata.topics[topic].error is not None:
            raise confluent_kafka.KafkaException(metadata.topics[topic].error)

        # Construct TopicPartition list of partitions to query
        partitions = [confluent_kafka.TopicPartition(topic, p) for p in metadata.topics[topic].partitions]
        # print(partitions)

        # for partition in partitions:
        #     print(consumer.get_watermark_offsets(partition))

       # localhost:9092 (ssh tunnel)
       # 10.3.2.33:9092 (ipfw 10.3.2.33 -> 127.0.0.1)


        # Query committed offsets for this group and the given partitions
        committed = consumer.committed(partitions, timeout=5)
        #
        # print(committed)
        for partition in committed:
            # Get the partitions low and high watermark offsets.
            (lo, hi) = consumer.get_watermark_offsets(partition, timeout=5, cached=False)

            if partition.offset == confluent_kafka.OFFSET_INVALID:
                offset = "-"
            else:
                offset = "%d" % (partition.offset)

            if hi < 0:
                lag = "no hwmark"  # Unlikely
            elif partition.offset < 0:
                # No committed offset, show total message count as lag.
                # The actual message count may be lower due to compaction
                # and record deletions.
                lag = "%d" % (hi - lo)
            else:
                lag = "%d" % (hi - partition.offset)

            print("%-50s  %9s  %9s" % (
                "{} [{}]".format(partition.topic, partition.partition), offset, lag))

    except Exception as e:
        consumer.close()

