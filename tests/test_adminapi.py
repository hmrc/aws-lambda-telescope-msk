from unittest import mock
from unittest.mock import Mock
from telemetry.telescope_msk.adminapi import list_consumer_groups, list_consumer_groups_excluding
from unittest.mock import MagicMock
from telemetry.telescope_msk.logger import get_app_logger


# # are we returning the list of groups
def test_list_consumer_groups():
    mock_group = Mock(
        id='id1',
        error=None
    )
    mock_groups = [mock_group]
    mock_client = MagicMock()
    mock_client.list_groups.return_value = mock_groups

    assert list_consumer_groups(mock_client) == mock_groups


# are we excluding consumer groups with errors
def test_list_consumer_groups_with_errors():
    mock_group = Mock(
        id='id1',
        error='test error'
    )
    mock_groups = [mock_group]
    mock_client = MagicMock()
    mock_client.list_groups.return_value = mock_groups

    assert len(list_consumer_groups(mock_client)) == 0


# are we logging consumer groups with errors
def test_list_consumer_groups_error_logging():
    logger = get_app_logger()
    with mock.patch.object(logger, 'error') as mock_logger:
        mock_error = 'test error'
        mock_group = Mock(
            id='id1',
            error=mock_error
        )
        mock_groups = [mock_group]
        mock_client = MagicMock()
        mock_client.list_groups.return_value = mock_groups

        list_consumer_groups(mock_client)

        mock_logger.assert_called_once_with(mock_error)


# are we excluding the consumer groups that are listed in exclude_groups

def test_list_consumer_groups_excluding_groups():
    exclude_groups = ['exclude_me']
    mock_groups = [Mock(id='id1', error=None), Mock(id='exclude_me', error=None)]
    print(mock_groups)

    mock_client = MagicMock()
    mock_client.list_groups.return_value = mock_groups

    assert len(list_consumer_groups_excluding(mock_client, exclude_groups)) == 1


