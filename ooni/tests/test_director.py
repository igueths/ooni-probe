from mock import patch, MagicMock

from ooni.settings import config
from ooni.director import Director

from twisted.internet import defer
from twisted.trial import unittest

class TestDirector(unittest.TestCase):
    def test_get_net_tests(self):
        director = Director()
        nettests = director.getNetTests()
        assert 'http_requests' in nettests
        assert 'dnsconsistency' in nettests
        assert 'http_header_field_manipulation' in nettests
        assert 'traceroute' in nettests
    
    def test_start_tor(self):
        from txtorcon import TorControlProtocol
        proto = MagicMock()
        proto.tor_protocol = TorControlProtocol()
        
        mock_TorState = MagicMock()
        # We use the instance of mock_TorState so that the mock caching will
        # return the same instance when TorState is created.
        mts = mock_TorState()
        mts.protocol.get_conf = lambda x: defer.succeed({'SocksPort': '4242'})
        mts.post_bootstrap = defer.succeed(mts)

        # Set the tor_protocol to be already fired
        state = MagicMock()
        proto.tor_protocol.post_bootstrap = defer.succeed(state)
        
        mock_launch_tor = MagicMock()
        mock_launch_tor.return_value = defer.succeed(proto)
        
        @patch('ooni.director.TorState', mock_TorState)
        @patch('ooni.director.launch_tor', mock_launch_tor)
        @defer.inlineCallbacks
        def director_start_tor():
            director = Director()
            yield director.startTor()
            assert config.tor.socks_port == 4242
            assert config.tor.control_port == 4242
            config.tor_state = None

        return director_start_tor()