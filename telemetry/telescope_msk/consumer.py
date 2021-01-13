import confluent_kafka
from telemetry.telescope_msk.msk import get_default_bootstrap_servers


def list_offsets():
    bootstrap_servers = get_default_bootstrap_servers()

    from confluent_kafka import Consumer

    consumer = Consumer({
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'metrics',
        'auto.offset.reset': 'earliest'
    })

    topic = 'metrics'

    metadata = consumer.list_topics(topic, timeout=10)
    if metadata.topics[topic].error is not None:
        raise confluent_kafka.KafkaException(metadata.topics[topic].error)