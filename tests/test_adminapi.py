from unittest import mock
from unittest.mock import patch, Mock

from telemetry.telescope_msk.msk import get_plaintext_bootstrap_servers
from telemetry.telescope_msk.adminapi import create_admin_client, list_consumer_groups, list_consumer_groups_excluding
from telemetry.telescope_msk import adminapi
from unittest.mock import MagicMock
from confluent_kafka import Consumer
from telemetry.telescope_msk.logger import get_app_logger


# # are we returning the list of groups
@patch('confluent_kafka.admin.AdminClient')
def test_list_consumer_groups(MockAdminClient):
    mock_group = Mock(
        id='id1',
        error=None
    )
    mock_groups = [mock_group]
    mock_client = MockAdminClient()
    mock_client.list_groups.return_value = mock_groups

    assert list_consumer_groups(mock_client) == mock_groups


# are we excluding consumer groups with errors
@patch('confluent_kafka.admin.AdminClient')
def test_list_consumer_groups_with_errors(MockAdminClient):
    mock_group = Mock(
        id='id1',
        error='test error'
    )
    mock_groups = [mock_group]
    mock_client = MockAdminClient({})
    mock_client.list_groups.return_value = mock_groups

    assert len(list_consumer_groups(mock_client)) == 0


# are we logging consumer groups with errors
@patch('confluent_kafka.admin.AdminClient')
def test_list_consumer_groups_error_logging(MockAdminClient):
    logger = get_app_logger()
    with mock.patch.object(logger, 'error') as mock_logger:
    # with mock.patch('telemetry.telescope_msk.adminapi', 'get_app_logger', return_value={'error': MagicMock(return_value=None)}) as mock_logger: does not work
        mock_error = 'test error'
        mock_group = Mock(
            id='id1',
            error=mock_error
        )
        mock_groups = [mock_group]
        mock_client = MockAdminClient({})
        mock_client.list_groups.return_value = mock_groups

        list_consumer_groups(mock_client)

        mock_logger.assert_called_once_with(mock_error)


# are we excluding the consumer groups that are listed in exclude_groups
@patch('confluent_kafka.admin.AdminClient')
def test_list_consumer_groups_excluding_groups(MockAdminClient):
    exclude_groups = ['exclude_me']
    mock_groups = [Mock(id='id1', error=None), Mock(id='exclude_me', error=None)]
    print(mock_groups)

    mock_client = MockAdminClient({})
    mock_client.list_groups.return_value = mock_groups

    assert len(list_consumer_groups_excluding(mock_client, exclude_groups)) == 1


