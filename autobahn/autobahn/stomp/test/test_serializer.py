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

# from twisted.trial import unittest
import unittest

from autobahn.stomp import message
from autobahn.stomp import serializer

def generate_test_messages():
    return [
        message.STOMP('test.com', '1.2'),
        message.Connect('test.com'),
        message.Connect('test.com', '1.2'),
	message.Connected('1.2'),
	message.Send('/test', u'test message'),
	message.Send('/test', u'test message', '123456'),
	message.Error(),
	message.Error('error message', u'detailed error message' '123456'),
	message.Receipt('123456')
    ]


class TestSerializer(unittest.TestCase):

	def setUp(self):
		self.serializer = serializer.Serializer()

    	def test_roundtrip(self):
        	for msg in generate_test_messages():
                	# serialize message
                	payload = self.serializer.serialize(msg)

                	# unserialize message again
                	msg2 = self.serializer.unserialize(payload, False)

			# clear the cache on the serialized object
			msg.uncache()

                	# must be equal: message roundtrips via the serializer
                	self.assertEqual(msg, msg2)

    	def test_caching(self):
        	for msg in generate_test_messages():
            		# message serialization cache is initially empty
            		self.assertEqual(msg._serialized, None)
                	# do the serialization
                	payload = self.serializer.serialize(msg)
                	# now the message serialization must be cached
                	self.assertNotEqual(msg._serialized, None)
                	# and after resetting the serialization cache, message
                	# serialization is gone
                	msg.uncache()
                	self.assertEquals(msg._serialized, None)

if __name__ == '__main__':
    unittest.main()
