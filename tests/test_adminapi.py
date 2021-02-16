from unittest import mock
from unittest.mock import patch

from telemetry.telescope_msk.msk import get_plaintext_bootstrap_servers
from telemetry.telescope_msk.adminapi import create_admin_client, list_consumer_groups, list_consumer_groups_excluding
from confluent_kafka.admin import AdminClient
from telemetry.telescope_msk import adminapi
from unittest.mock import MagicMock
from confluent_kafka import Consumer
from telemetry.telescope_msk.logger import get_app_logger


# # are we returning the list of groups
def test_list_consumer_groups():
    mock_groups = [{'id': 'id1', 'error': None}]
    mock_client = AdminClient({})
    mock_client.list_groups = MagicMock(return_value=mock_groups)

    assert list_consumer_groups(mock_client) == mock_groups


# are we excluding consumer groups with errors
def test_list_consumer_groups_with_errors():
    mock_groups = [{'id': 'id1',
                    'error': 'test error'
                    }]
    mock_client = AdminClient({})
    mock_client.list_groups = MagicMock(return_value=mock_groups)

    assert len(list_consumer_groups(mock_client)) == 0


# are we logging consumer groups with errors
def test_list_consumer_groups_error_logging():

    with mock.patch('telemetry.telescope_msk.adminapi', 'error') as mock_logger:
        mock_error = 'test error'
        mock_groups = [{'id': 'id1',
                        'error': mock_error
                        }]
        mock_client = AdminClient({})
        mock_client.list_groups = MagicMock(return_value=mock_groups)

        list_consumer_groups(mock_client)

        mock_logger.assert_called_once_with(mock_error)


# are we excluding the consumer groups that are listed in exclude_groups



