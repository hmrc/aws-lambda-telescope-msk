################################### VVVVVVV from https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/list_offsets.py
    print("%-50s  %9s  %9s" % ("Topic [Partition]", "Committed", "Lag"))
    print("=" * 72)

    for topic in sys.argv[3:]:
        # Get the topic's partitions
        metadata = consumer.list_topics(topic, timeout=10)
        if metadata.topics[topic].error is not None:
            raise confluent_kafka.KafkaException(metadata.topics[topic].error)

        # Construct TopicPartition list of partitions to query
        partitions = [confluent_kafka.TopicPartition(topic, p) for p in metadata.topics[topic].partitions]

        # Query committed offsets for this group and the given partitions
        committed = consumer.committed(partitions, timeout=10)

        for partition in committed:
            # Get the partitions low and high watermark offsets.
            (lo, hi) = consumer.get_watermark_offsets(partition, timeout=10, cached=False)

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

    consumer.close()


###is this how to glean all metrics? check metrics available to partition and consumer?

    ##################### or VVVVVVVV from https://www.confluent.io/blog/introduction-to-apache-kafka-for-python-programmers/
    consumer.subscribe(metadata) ##or should this be ([metadata]) or (['metadata'])

    try:
        while True:
            msg = consumer.poll(0.1)
            if msg is None:
                continue
            elif not msg.error():
                print('Received message: {0}'.format(msg.value()))
            elif msg.error().code() == KafkaError._PARTITION_EOF:
                print('End of partition reached {0}/{1}'
                      .format(msg.topic(), msg.partition()))
            else:
                print('Error occured: {0}'.format(msg.error().str()))

    except KeyboardInterrupt:
        pass

    finally:
        consumer.close()
