from unittest.mock import MagicMock, Mock
from unittest import mock

import confluent_kafka

from telemetry.telescope_msk.consumer import get_consumer, get_committed_partitions_for_topic, \
    return_metrics_for_partition
from confluent_kafka import Consumer
from telemetry.telescope_msk.logger import get_app_logger


def test_get_consumer():
    consumer = get_consumer(bootstrap_servers="test bootstrap arn")
    assert type(consumer) == Consumer


def test_get_committed_partitions_for_topic_with_error():
    consumer = MagicMock()
    logger = get_app_logger()
    with mock.patch.object(logger, 'error') as mock_logger:
        mock_error = 'test error message'
        mock_topic = Mock(
            topic='name',
            partitions={},
            error=mock_error
            )

        get_committed_partitions_for_topic(consumer, mock_topic)

        mock_logger.assert_called_once_with(mock_error)


# what topics are being filtered out in list_offsets
# can we do this with pattern matching? if so we should do this in  get_groups_excluding


# test that hi being less than 0 returns a lag of none
def test_negative_high_watermark():
    consumer = MagicMock()
    consumer.get_watermark_offsets.return_value = (0, -10)
    partition = Mock(offset=10)

    metrics = return_metrics_for_partition(consumer, partition)

    assert metrics.get('Lag') is None


# test that partition offset being less than 0 returns hi - low
def test_negative_partition_offset():
    # OFFSET_INVALID, OFFSET_STORED, OFFSET_END, and OFFSET_BEGINNING are all numerical consts that are < 0
    consumer = MagicMock()
    consumer.get_watermark_offsets.return_value = (5, 9)

    assert return_metrics_for_partition(consumer, Mock(offset=-1)) == {'High': 9, 'Low': 5, 'Lag': 4}


# test that if hi >=0 and partition offset >0 we return hi - offset
def test_returns_normal_lag():
    consumer = MagicMock()
    consumer.get_watermark_offsets.return_value = (5, 9)

    assert return_metrics_for_partition(consumer, Mock(offset=0)) == {'High': 9, 'Low': 5, 'Lag': 9}


# test that if an error is raised we log it
def test_logs_errors():
    logger = get_app_logger()
    with mock.patch.object(logger, 'error') as mock_logger:
        mock_error = Exception('test error')
        consumer = MagicMock()
        consumer.get_watermark_offsets.side_effect = mock_error

        return_metrics_for_partition(consumer, Mock(offset=0)) == {'High': 9, 'Low': 5, 'Lag': 9}

        mock_logger.assert_called_once_with(mock_error)
