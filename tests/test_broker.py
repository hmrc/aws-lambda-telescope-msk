from unittest import TestCase
from unittest.mock import patch

from telemetry.telescope_msk.broker import ping_brokers


class PingBrokers(TestCase):
    def test_pings_brokers_in_comma_deliminated_string(self):
        with patch('telemetry.telescope_msk.broker.ping_broker') as mock_ping:
            ping_brokers('broker1,broker2,broker3')

            mock_ping.assert_any_call('broker1')
            mock_ping.assert_any_call('broker2')
            mock_ping.assert_any_call('broker3')
