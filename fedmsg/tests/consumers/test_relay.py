import os
import unittest

import mock

from fedmsg.consumers import relay


class TestSigningRelayConsumer(unittest.TestCase):
    """Tests for the :class:`fedmsg.consumers.relays.SigningRelayConsumer`."""

    def setUp(self):
        self.hub = mock.Mock()
        self.signing_cert = (
            u'LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUVVekNDQTd5Z0F3SUJBZ0lCRHpBTkJna3Fo\n'
            u'a2lHOXcwQkFRVUZBRENCb0RFTE1Ba0dBMVVFQmhNQ1ZWTXgKQ3pBSkJnTlZCQWdUQWs1RE1SQXdE\n'
            u'Z1lEVlFRSEV3ZFNZV3hsYVdkb01SY3dGUVlEVlFRS0V3NUdaV1J2Y21FZwpVSEp2YW1WamRERVBN\n'
            u'QTBHQTFVRUN4TUdabVZrYlhObk1ROHdEUVlEVlFRREV3Wm1aV1J0YzJjeER6QU5CZ05WCkJDa1RC\n'
            u'bVpsWkcxelp6RW1NQ1FHQ1NxR1NJYjNEUUVKQVJZWFlXUnRhVzVBWm1Wa2IzSmhjSEp2YW1WamRD\n'
            u'NXYKY21jd0hoY05NVEl3TnpFMU1qRXhPRFV5V2hjTk1qSXdOekV6TWpFeE9EVXlXakNCNGpFTE1B\n'
            u'a0dBMVVFQmhNQwpWVk14Q3pBSkJnTlZCQWdUQWs1RE1SQXdEZ1lEVlFRSEV3ZFNZV3hsYVdkb01S\n'
            u'Y3dGUVlEVlFRS0V3NUdaV1J2CmNtRWdVSEp2YW1WamRERVBNQTBHQTFVRUN4TUdabVZrYlhObk1U\n'
            u'QXdMZ1lEVlFRREV5ZHphR1ZzYkMxd1lXTnIKWVdkbGN6QXhMbkJvZURJdVptVmtiM0poY0hKdmFt\n'
            u'VmpkQzV2Y21jeE1EQXVCZ05WQkNrVEozTm9aV3hzTFhCaApZMnRoWjJWek1ERXVjR2g0TWk1bVpX\n'
            u'UnZjbUZ3Y205cVpXTjBMbTl5WnpFbU1DUUdDU3FHU0liM0RRRUpBUllYCllXUnRhVzVBWm1Wa2Iz\n'
            u'SmhjSEp2YW1WamRDNXZjbWN3Z1o4d0RRWUpLb1pJaHZjTkFRRUJCUUFEZ1kwQU1JR0oKQW9HQkFN\n'
            u'RUlKNURzZ0VsaG5XMENLcnNpc1UvV0svUFBrSkNST0N0WnBwQXZha0dDVHhVU1RoWDhpZmVsVjVa\n'
            u'dwp1T1dCWDlxTHg2cGJzNHhodnVrVDkwUHphYUlKR24xeUpjVnZLTDYzS1I1SCtZNXdOamJLREhY\n'
            u'ZlBuM0J1Z0hSCmRzdnV0Yi9Fa3hNM3NYbnRpZWY0K2ZWVGsyanZiTXFsYmEvWHc4cXBsRWxqMXFm\n'
            u'aEFnTUJBQUdqZ2dGWE1JSUIKVXpBSkJnTlZIUk1FQWpBQU1DMEdDV0NHU0FHRytFSUJEUVFnRmg1\n'
            u'RllYTjVMVkpUUVNCSFpXNWxjbUYwWldRZwpRMlZ5ZEdsbWFXTmhkR1V3SFFZRFZSME9CQllFRkUw\n'
            u'Zmh6czZhWjViVDJVNjZzUjNrUG1LdzBGYk1JSFZCZ05WCkhTTUVnYzB3Z2NxQUZBQ1lwZFhueEZV\n'
            u'T2hLTm4vbVpLRnVBRUZkMGhvWUdtcElHak1JR2dNUXN3Q1FZRFZRUUcKRXdKVlV6RUxNQWtHQTFV\n'
            u'RUNCTUNUa014RURBT0JnTlZCQWNUQjFKaGJHVnBaMmd4RnpBVkJnTlZCQW9URGtabApaRzl5WVNC\n'
            u'UWNtOXFaV04wTVE4d0RRWURWUVFMRXdabVpXUnRjMmN4RHpBTkJnTlZCQU1UQm1abFpHMXpaekVQ\n'
            u'Ck1BMEdBMVVFS1JNR1ptVmtiWE5uTVNZd0pBWUpLb1pJaHZjTkFRa0JGaGRoWkcxcGJrQm1aV1J2\n'
            u'Y21Gd2NtOXEKWldOMExtOXlaNElKQUk3cktOaXBFNTE4TUJNR0ExVWRKUVFNTUFvR0NDc0dBUVVG\n'
            u'QndNQ01Bc0dBMVVkRHdRRQpBd0lIZ0RBTkJna3Foa2lHOXcwQkFRVUZBQU9CZ1FCK3RlWFNCV0pQ\n'
            u'VWlLMDBEYWl4RmF6ZThSUW01S1ZBQjBRCkRSdDdqcDdRcVViZHd2ZWhvU3NKODVDYnZLazhYZ0Ey\n'
            u'UW16RFdhRzRhcklrQUVCWGFkNjlyMkZmMTMzTmQxQlEKeGZGRGRWdXFyeE9HeXJwazhyOFAxYmJJ\n'
            u'YjRNb09aUVQxbGFGTFUzZjNJUVNIYW93RkRuZ0V0azlZUzRpSEhrWQora3FlRnczYmhRPT0KLS0t\n'
            u'LS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=\n'
        )
        self.hub.config = {
            'fedmsg.consumers.relay.enabled': True,
            'validate_signatures': False,
            'ssldir': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_certs/keys'),
        }

    @mock.patch('fedmsg.consumers.relay.log')
    def test_initialization(self, mock_log):
        """Assert that when the certnames dictionary is mis-configured an error is logged."""
        relay.SigningRelayConsumer(self.hub)
        mock_log.error.assert_called_once_with(
            'The signing relay requires that the certificate name is in '
            'the "certnames" dictionary using the "signing_relay" key')

    def test_message_signed(self):
        """Assert messages are signed prior to relay."""
        self.hub.config['certnames'] = {
            'signing_relay': 'shell-packages01.phx2.fedoraproject.org',
        }
        expected_msg = {
            'my': 'msg',
            'crypto': 'x509',
            'signature': (u'kyZ496SD+qgufonX9lqV/4L/o3s0+j4j5RaeMzhRIIGhfk6/RIEtl1DW73xbo+'
                          u'Xs2STbidFyz7Yt\n6IUb3/U+8Io0CTTbIyQvcvtof/a3EdmbnZtOQ93VfnXXkn'
                          u'6m76yVcFnQDicagY/600KmfNCDAwve\nI6+B9va/q10CBloMLkE=\n'),
            'certificate': self.signing_cert,
        }
        consumer = relay.SigningRelayConsumer(self.hub)
        consumer.consume({'topic': 'testtopic', 'body': {'my': 'msg'}})
        self.hub.send_message.assert_called_once_with(topic='testtopic', message=expected_msg)
