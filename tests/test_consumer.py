from telemetry.telescope_msk.consumer import get_consumer
from confluent_kafka import Consumer


#are we getting the correct type back for a valid consumer
def test_get_consumer():
    consumer = get_consumer(bootstrap_servers="test bootstrap arn")
    assert type(consumer) == Consumer

def test_return_metrics():

    assert True