import json
import os
from datetime import datetime

from aws_lambda_powertools import Logger
from confluent_kafka import Producer

logger = Logger(service="telescope-msk-producer")


def get_env_bootstrap_servers():
    return os.environ.get("BOOTSTRAP_BROKERS")


def get_topic_from_event(event):
    kafka_topic = "logs"

    try:
        kafka_topic = event["topic"]
    except KeyError:
        logger.debug("No topic in event, defaulting to kafka_topic=logs")

    return kafka_topic


def get_data_from_event(event):
    data = {"data0": "hello", "data1": "world"}

    try:
        data = event["data"]
    except KeyError:
        logger.debug("No data in event, defaulting to noddy hello world object")

    return data


producer = Producer(
    {
        "api.version.request": "false",
        "bootstrap.servers": get_env_bootstrap_servers(),
        "broker.version.fallback": "0.9.0",
        "message.max.bytes": 1000000000,
        "security.protocol": "SSL",
        "socket.timeout.ms": 100,
    }
)


def lambda_handler(event, context):
    try:
        logger.info(f"Lambda Request ID: {context.aws_request_id}")
    except AttributeError:
        logger.debug("No context object available")

    # Get details from the event object
    kafka_topic = get_topic_from_event(event)
    data = get_data_from_event(event)

    # Calculate elapsed time
    start_time = datetime.now()
    send_msg_async(kafka_topic, data)
    end_time = datetime.now()

    # Display elapsed time
    time_delta = end_time - start_time
    logger.info("Time taken to complete = %s seconds" % time_delta.total_seconds())


def delivery_report(err, message):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {message.topic()} [{message.partition()}]")


def send_msg_async(topic, message):
    logger.debug("Sending message")
    try:
        msg_json_str = str({"data": json.dumps(message)})
        producer.produce(
            topic,
            msg_json_str,
            callback=lambda err, original_msg=msg_json_str: delivery_report(
                err, original_msg
            ),
        )
        producer.flush()
    except Exception as e:
        logger.error(f"Failed to produce and flush message: {e}")
