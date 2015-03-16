###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from __future__ import absolute_import

import sys

from autobahn.stomp import message
from autobahn.stomp.exception import ProtocolError

if sys.version_info < (2, 7):
    # noinspection PyUnresolvedReferences
    import unittest2 as unittest
else:
    # from twisted.trial import unittest
    import unittest


class Foo:
    pass

class TestConnectMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Connect('test.com')
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
	self.assertEqual(msg[0], message.Connect.MESSAGE_TYPE)
        self.assertEqual(0, cmp(msg[1], {'host' : 'test.com', 'accept-version': '1.2'}))
        self.assertEqual(msg[2], None)

        e = message.Connect('test.com', None)
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
	self.assertEqual(msg[0], message.Connect.MESSAGE_TYPE)
        self.assertEqual(0, cmp(msg[1], {'host' : 'test.com'}))
        self.assertEqual(msg[2], None)


    def test_parse_and_marshal(self):
	headers = {'host' : 'test.com'}
	body = None
	msg = message.Connect.parse(headers, body)
        self.assertIsInstance(msg, message.Connect)
        self.assertEqual(msg.host, 'test.com')
        self.assertEqual(msg.marshal(), [message.Connect.MESSAGE_TYPE, headers, body])

class TestConnectedMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Connected('1.2')
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
	self.assertEqual(msg[0], message.Connected.MESSAGE_TYPE)
        self.assertEqual(0, cmp(msg[1], {'version' : '1.2'}))
        self.assertEqual(msg[2], None)

    def test_parse_and_marshal(self):
	headers = {'version' : '1.2'}
	body = None
	msg = message.Connected.parse(headers, body)
        self.assertIsInstance(msg, message.Connected)
        self.assertEqual(msg.version, '1.2')
        self.assertEqual(msg.marshal(), [message.Connected.MESSAGE_TYPE, headers, body])

class TestSendMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Send('/test', u'payload')
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
	self.assertEqual(msg[0], message.Send.MESSAGE_TYPE)
        self.assertEqual(0, cmp(msg[1], {'destination' : '/test'}))
        self.assertEqual(msg[2], u'payload')

        e = message.Send('/test', u'payload', '123456')
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
	self.assertEqual(msg[0], message.Send.MESSAGE_TYPE)
        self.assertEqual(0, cmp(msg[1], {'destination' : '/test', 'receipt' : '123456'}))
        self.assertEqual(msg[2], u'payload')
	
    def test_parse_and_marshal(self):
	headers = {'destination' : '/test'}
	body = u'payload'
	msg = message.Send.parse(headers, body)
        self.assertIsInstance(msg, message.Send)
        self.assertEqual(msg.destination, '/test')
	self.assertEqual(msg.receipt, None)
        self.assertEqual(msg.body, u'payload')
        self.assertEqual(msg.marshal(), [message.Send.MESSAGE_TYPE, headers, body])

	headers = {'destination' : '/test', 'receipt' : '123456'}
	body = u'payload'
	msg = message.Send.parse(headers, body)
        self.assertIsInstance(msg, message.Send)
        self.assertEqual(msg.destination, '/test')
	self.assertEqual(msg.receipt, '123456')
        self.assertEqual(msg.body, u'payload')
        self.assertEqual(msg.marshal(), [message.Send.MESSAGE_TYPE, headers, body]) 

class TestReceiptMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Receipt('123456')
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
	self.assertEqual(msg[0], message.Receipt.MESSAGE_TYPE)
        self.assertEqual(0, cmp(msg[1], {'receipt-id' : '123456'}))
        self.assertEqual(msg[2], None)
	
    def test_parse_and_marshal(self):
	headers = {'receipt-id' : '123456'}
	body = None
	msg = message.Receipt.parse(headers, body)
        self.assertIsInstance(msg, message.Receipt)
	self.assertEqual(msg.receipt_id, '123456')
        self.assertEqual(msg.marshal(), [message.Receipt.MESSAGE_TYPE, headers, body]) 

class TestErrorMessage(unittest.TestCase):

    def test_ctor(self):
        e = message.Error('unspecified error', '123456', u'huge error')
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
	self.assertEqual(msg[0], message.Error.MESSAGE_TYPE)
        self.assertEqual(0, cmp(msg[1], {'message' : 'unspecified error', 'receipt-id' : '123456'}))
        self.assertEqual(msg[2], u'huge error')

        e = message.Error()
        msg = e.marshal()
        self.assertEqual(len(msg), 3)
	self.assertEqual(msg[0], message.Error.MESSAGE_TYPE)
        self.assertEqual(0, cmp(msg[1], {}))
        self.assertEqual(msg[2], None)
	
    def test_parse_and_marshal(self):
	headers = {'message' : 'unspecified error', 'receipt-id' : '123456'}
	body = u'huge error'
	msg = message.Error.parse(headers, body)
        self.assertIsInstance(msg, message.Error)
        self.assertEqual(msg.message, 'unspecified error')
        self.assertEqual(msg.receipt_id, '123456')
        self.assertEqual(msg.body, u'huge error')
        self.assertEqual(msg.marshal(), [message.Error.MESSAGE_TYPE, headers, body])

	headers = {'message' : 'unspecified error', 'receipt-id' : '123456'}
	body = None
	msg = message.Error.parse(headers, body)
        self.assertIsInstance(msg, message.Error)
        self.assertEqual(msg.message, 'unspecified error')
        self.assertEqual(msg.receipt_id, '123456')
        self.assertEqual(msg.body, None)
        self.assertEqual(msg.marshal(), [message.Error.MESSAGE_TYPE, headers, body])
        
if __name__ == '__main__':
    unittest.main()
