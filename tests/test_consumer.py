from unittest.mock import MagicMock
from unittest import mock
from telemetry.telescope_msk.consumer import get_consumer, list_offsets, get_committed_partitions_for_topic
from confluent_kafka import Consumer
from telemetry.telescope_msk.logger import get_app_logger
from unittest.mock import patch

def test_get_consumer():
    consumer = get_consumer(bootstrap_servers="test bootstrap arn")
    assert type(consumer) == Consumer

# def test_list_offsets():
#     # mock consumer.list topics to return metadata{topics} with no errors
#     mock_metadata = {'topics': [{
#         'topic': 'name',
#         'partitions': {
#         },
#         'error': None
#         }
#     ]
#     }
#     mock_client = Consumer()
#     mock_client.list_topics = MagicMock(return_value=mock_metadata)
#
#     # mock confluent_kafka.TopicPartition(topic, p) maybe we don't need this
#
#     # mock consumer.committed(partitions, timeout=10)
#     mock_committed = [{
#         'topic': 'some_topic',
#         'id': 1,
#         'offset':0
#     }]
#     mock_client.committed = MagicMock(return_value=mock_committed)
#
#
#     assert False

# @patch('confluent_kafka.admin.TopicMetadata')
# @patch('confluent_kafka.admin.ClusterMetadata')
# @patch('confluent_kafka.Consumer')
# def test_list_topic_errors(MockConsumer, MockTopicPartition, MockTopicMetadata):
#     logger = get_app_logger()
#     with mock.patch.object(logger, 'error') as mock_logger:
#         mock_error = 'test error message'
#
#         mock_topic = MockTopicMetadata()
#         mock_topic.name = 'name'
#         mock_topic.partitions = {}
#         mock_topic.error = mock_error
#
#         mock_metadata = MockTopicPartition()
#         mock_metadata.topics = {'name': mock_topic}
#
#         mock_consumer = MockConsumer()
#         mock_consumer.list_topics = MagicMock(return_value=mock_metadata)
#
#         list_offsets(mock_consumer)
#
#         mock_logger.assert_called_once_with(mock_error)

# def test_return_metrics():
#
#     assert False

@patch('confluent_kafka.Consumer') #can we get away with just using Mock and not patching here?
@patch('confluent_kafka.admin.TopicMetadata')
def test_get_committed_partitions_for_topic_with_error(MockTopicMetadata, MockConsumer):
    consumer = MockConsumer()
    consumer.committed = MagicMock()
    logger = get_app_logger()
    with mock.patch.object(logger, 'error') as mock_logger:
        mock_error = 'test error message'
        mock_topic = MockTopicMetadata()
        mock_topic.topic = 'name'
        mock_topic.partitions = {}
        mock_topic.error = mock_error

        get_committed_partitions_for_topic(consumer, mock_topic)

        mock_logger.assert_called_once_with(mock_error)















