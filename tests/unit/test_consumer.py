from unittest import mock
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from confluent_kafka import Consumer
from telescope_msk.consumer import get_consumer
from telescope_msk.consumer import get_metrics_for_group_and_topic
from telescope_msk.consumer import get_metrics_for_groups_and_topics
from telescope_msk.consumer import get_metrics_for_partition
from telescope_msk.consumer import get_metrics_for_partitions
from telescope_msk.consumer import get_metrics_for_topic
from telescope_msk.consumer import get_partitions_for_topic
from telescope_msk.consumer import get_partitions_for_topics
from telescope_msk.logger import get_app_logger


class GetConsumer(TestCase):
    def test_get_consumer(self):
        consumer = get_consumer(bootstrap_servers="test bootstrap arn", group_id="test")
        self.assertEqual(type(consumer), Consumer)


#
#
class GetMetricsForGroupsAndTopics:
    def test_calls_get_metrics_for_group_and_topic_for_each_key_value(self):
        with patch(
            "telescope_msk.consumer.get_metrics_for_group_and_topic"
        ) as mock_get_metrics:
            consumer_groups_topic_names = {"group1", "topic1"}

            get_metrics_for_groups_and_topics(consumer_groups_topic_names)

            mock_get_metrics.assert_called_with("group1", "topic1")


class GetMetricsForGroupAndTopic(TestCase):
    def test_creates_consumer_on_group(self):
        # consumer must be on the group otherwise partition offsets can't be read and are returned as OFFSET_INVALID
        with patch("telescope_msk.consumer.get_consumer") as mock_get_consumer:

            get_metrics_for_group_and_topic("bootstrap_servers", "group", "topic")

            mock_get_consumer.assert_called_with("bootstrap_servers", "group")

    def test_calls_get_metrics_for_topic(self):
        # consumer must be on the group otherwise partition offsets can't be read and are returned as OFFSET_INVALID
        with patch("telescope_msk.consumer.get_consumer") as mock_get_consumer:
            mock_consumer = MagicMock()
            mock_get_consumer.return_value = mock_consumer
            with patch("telescope_msk.consumer.get_metrics_for_topic") as get_metrics:
                get_metrics.return_value = [{"metrics": "foo"}]
                out = get_metrics_for_group_and_topic(
                    "bootstrap_servers", "group", "topic"
                )

                get_metrics.assert_called_with(mock_consumer, "topic")
                self.assertEqual(out[0]["metrics"], "foo")


# class GetMetricsForTopic:
#     def test(self):
#         assert True


class GetPartitionsForTopic(TestCase):
    def test_topic_error_returns_empty_list(self):
        out = get_partitions_for_topic(Mock(error="Error"))
        self.assertEqual(out, [])

    def test_topic_error_is_logged(self):
        logger = get_app_logger()
        with mock.patch.object(logger, "error"):
            mock_error = "Error"

            get_partitions_for_topic(Mock(error=mock_error))

            logger.error.assert_called_with(mock_error)

    def test_TopicPartitions_are_created(self):
        # with patch('confluent_kafka.TopicPartition') as mockTopicPartition:
        with patch("telescope_msk.consumer.TopicPartition") as mockTopicPartition:

            test_topic = "test_topic_01"
            mock_partition = 6

            get_partitions_for_topic(
                Mock(error=None, topic=test_topic, partitions=[mock_partition])
            )

            mockTopicPartition.assert_called_with(test_topic, mock_partition)


class GetPartitionsForTopics(TestCase):
    def test_calls_through_for_each_topic(self):
        with patch("telescope_msk.consumer.get_partitions_for_topic") as get_partitions:
            get_partitions.return_value = []
            mock_topics = {
                "test_topic_1": Mock(
                    error="error1", topic="test_topic_1", partitions=[1]
                ),
                "test_topic_2": Mock(
                    error="error2", topic="test_topic_2", partitions=[2]
                ),
            }
            get_partitions_for_topics(Mock(topics=mock_topics))

            get_partitions.assert_any_call(mock_topics["test_topic_2"])
            get_partitions.assert_any_call(mock_topics["test_topic_1"])


class GetMetricsForPartitions(TestCase):
    def test_calls_through_for_each_partition(self):
        consumer = MagicMock()
        with patch("telescope_msk.consumer.get_metrics_for_partition") as get_metrics:
            get_metrics.return_value = {"offset": 10}

            out = get_metrics_for_partitions(consumer, [Mock(), Mock()])

            self.assertEqual(out, [{"offset": 10}, {"offset": 10}])


class GetMetricsForPartition(TestCase):
    # test that hi being less than 0 returns a lag of none
    def test_negative_high_watermark(self):
        consumer = MagicMock()
        consumer.get_watermark_offsets.return_value = (0, -10)
        partition = Mock(offset=10)

        metrics = get_metrics_for_partition(consumer, partition)

        self.assertEqual(metrics.get("lag"), 0)

    # test that partition offset being less than 0 returns hi - low
    def test_negative_partition_offset(self):
        # OFFSET_INVALID, OFFSET_STORED, OFFSET_END, and OFFSET_BEGINNING are all numerical consts that are < 0
        consumer = MagicMock()
        consumer.get_watermark_offsets.return_value = (5, 9)

        self.assertEqual(
            get_metrics_for_partition(
                consumer, Mock(offset=-1, partition=11, topic="test_topic")
            ),
            {
                "partition_id": 11,
                "topic_name": "test_topic",
                "high": 9,
                "low": 5,
                "lag": 4,
                "offset": -1,
            },
        )

    # test that if hi >=0 and partition offset >0 we return hi - offset
    def test_returns_normal_lag(self):
        consumer = MagicMock()
        consumer.get_watermark_offsets.return_value = (5, 9)

        self.assertEqual(
            get_metrics_for_partition(
                consumer, Mock(offset=0, partition=11, topic="test_topic")
            ),
            {
                "partition_id": 11,
                "topic_name": "test_topic",
                "high": 9,
                "low": 5,
                "lag": 9,
                "offset": 0,
            },
        )

    # test that if an error is raised we log it
    def test_raises_exception_on_None(self):
        consumer = MagicMock()
        consumer.get_watermark_offsets.return_value = None

        l = lambda _: get_metrics_for_partition(
            consumer, Mock(offset=-1, partition=11, topic="test_topic")
        )
        self.assertRaises(Exception, l)
