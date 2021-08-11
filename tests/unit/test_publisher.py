from unittest.mock import patch
from src.telescope_msk.publisher import publish_metrics, publish_metric_sums


@patch("src.telescope_msk.publisher.publish_kafka_to_graphite")
def test_publish_metrics(mock_publish):

    publish_metrics(
        [
            {
                "partition_id": 11,
                "topic_name": "test_topic",
                "high": 9,
                "low": 5,
                "lag": 4,
                "offset": -1,
            }
        ],
        "graphite",
    )
    assert mock_publish.call_count == 4
    mock_publish.assert_any_call("test_topic.partition_11.high", 9, "graphite")
    mock_publish.assert_any_call("test_topic.partition_11.low", 5, "graphite")
    mock_publish.assert_any_call("test_topic.partition_11.lag", 4, "graphite")
    mock_publish.assert_any_call("test_topic.partition_11.offset", -1, "graphite")


@patch("src.telescope_msk.publisher.publish_kafka_to_graphite")
def test_publish_metric_sums(mock_publish):
    publish_metric_sums(
        [
            {
                "partition_id": 11,
                "topic_name": "test_topic1",
                "high": 9,
                "low": 2,
                "lag": 4,
                "offset": -1,
            },
            {
                "partition_id": 11,
                "topic_name": "test_topic1",
                "high": 1,
                "low": 3,
                "lag": 4,
                "offset": -1,
            },
            {
                "partition_id": 11,
                "topic_name": "test_topic2",
                "high": 5,
                "low": 2,
                "lag": 4,
                "offset": -1,
            },
            {
                "partition_id": 11,
                "topic_name": "test_topic2",
                "high": 1,
                "low": 2,
                "lag": 3,
                "offset": -1,
            },
        ],
        "graphite",
    )

    mock_publish.assert_any_call("test_topic1.sum-high", 10, "graphite")
    mock_publish.assert_any_call("test_topic1.sum-low", 5, "graphite")
    mock_publish.assert_any_call("test_topic1.sum-lag", 8, "graphite")
    mock_publish.assert_any_call("test_topic1.sum-range", 5, "graphite")
    mock_publish.assert_any_call("test_topic2.sum-high", 6, "graphite")
    mock_publish.assert_any_call("test_topic2.sum-low", 4, "graphite")
    mock_publish.assert_any_call("test_topic2.sum-lag", 7, "graphite")
    mock_publish.assert_any_call("test_topic2.sum-range", 2, "graphite")
