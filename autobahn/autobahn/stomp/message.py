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

import re
import six

import autobahn
from autobahn import util
from autobahn.stomp.exception import ProtocolError
from autobahn.stomp.interfaces import IMessage

__all__ = (u'STOMP',
           u'Connect',
           u'Connected',
           u'Send',
           u'Disconnect',
           u'Receipt',
           u'Error')


class Message(util.EqualityMixin):
	"""
	STOMP message base class. Implements :class:`autobahn.stomp.interfaces.IMessage`.

	.. note:: This is not supposed to be instantiated.
    	"""

    	def __init__(self):
        	# serialization cache: mapping from ISerializer instances to serialized bytes
        	self._serialized = None

    	def uncache(self):
        	"""
        	Implements :func:`autobahn.stomp.interfaces.IMessage.uncache`
        	"""
        	self._serialized = None


	def serialize(self):
        	"""
        	Implements :func:`autobahn.stomp.interfaces.IMessage.serialize`
        	"""
		# only serialize if not cached ..
        	if self._serialized is None:
            		self._serialized = self.marshal()
        	return self._serialized;

IMessage.register(Message)


class STOMP(Message):
    """
    A STOMP ``STOMP`` message.
    """

    MESSAGE_TYPE = "STOMP"
    """
    The STOMP message code for this type of message.
    """

    def __init__(self, host, accept_version):
        """
        :param host: name of host the client wishes to connect to. 
        :type host: string
        :param accept_version: versions of the protocol the client can accept
        :type accept_version: string
        """
        assert(isinstance(host, six.string_types))
	assert(isinstance(accept_version, six.string_types))
        Message.__init__(self)
        self.host = host
	self.accept_version = accept_version 

    @staticmethod
    def parse(headers, body):
        """
        Verifies and parses an unserialized raw message into an actual STOMP message instance.
        """
	if 'host' in headers:
        	host = headers['host']
	else:
        	raise ProtocolError("missing host in STOMP")
	if 'accept-version' in headers:
		accept_version = headers['accept-version']
	else:
        	raise ProtocolError("missing accept-version in STOMP")
        obj = STOMP(host, accept_version)
        return obj

    def marshal(self):
        """
        Implements :func:`autobahn.stomp.interfaces.IMessage.marshal`
        """
	headers = {'host' : self.host, 'accept-version' : self.accept_version}
        return [STOMP.MESSAGE_TYPE, headers, None]

    def __str__(self):
        """
        Implements :func:`autobahn.stomp.interfaces.IMessage.__str__`
        """
        return "STOMP STOMP Message (accept-version = {0}, host = {1})".format(self.accept_version, self.host)

class Connect(Message):
	"""
    	A STOMP ``CONNECT`` message.
    	"""

    	MESSAGE_TYPE = "CONNECT"
    	"""
   	The STOMP message code for this type of message.
   	"""

 	def __init__(self, host, accept_version = '1.2'):
        	"""
        	:param host: name of host the client wishes to connect to. 
        	:type host: string
        	:param accept_version: versions of the protocol the client can accept
        	:type accept_version: string
        	"""
        	assert(isinstance(host, six.string_types))
        	assert(accept_version is None or isinstance(accept_version, six.string_types))
        	Message.__init__(self)
        	self.accept_version = accept_version
        	self.host = host

	@staticmethod
	def parse(headers, body):
        	"""
        	Verifies and parses an unserialized raw message into an actual STOMP message instance.
        	"""
		if 'host' in headers:
			host = headers['host']
		else:
        		raise ProtocolError("missing host in CONNECT")
		if 'accept-version' in headers:
			accept_version = headers['accept-version']
		else:
			accept_version = None
        	obj = Connect(host, accept_version)
        	return obj	

    	def marshal(self):
 		"""
        	Implements :func:`autobahn.stomp.interfaces.IMessage.marshal`
        	"""
		headers = {'host' : self.host}
		if self.accept_version is not None:
			headers['accept-version'] = self.accept_version
        	return [Connect.MESSAGE_TYPE, headers, None]

    	def __str__(self):
        	"""
        	Implements :func:`autobahn.stomp.interfaces.IMessage.__str__`
        	"""
        	return "STOMP CONNECT Message (accept-version = {0}, host = {1})".format(self.accept_version, self.host)

class Connected(Message):
    """
    A STOMP ``CONNECTED`` message.
    """

    MESSAGE_TYPE = "CONNECTED"
    """
   The STOMP message code for this type of message.
   """

    def __init__(self, version):
        """
        :param version: protocol version accepted by the server.
        :type reason: string
        """
        assert(isinstance(version, six.string_types))

        Message.__init__(self)
        self.version = version

    @staticmethod
    def parse(headers, body):
        """
        Verifies and parses an unserialized raw message into an actual STOMP message instance.
	"""
	if 'version' in headers:
		version = headers['version']
	else:
       		raise ProtocolError("missing version in CONNECTED")
        obj = Connected(version)
        return obj

    def marshal(self):
        """
        Implements :func:`autobahn.stomp.interfaces.IMessage.marshal`
        """
	headers = {'version' : self.version}
        return [Connected.MESSAGE_TYPE, headers, None]

    def __str__(self):
        """
        Implements :func:`autobahn.stomp.interfaces.IMessage.__str__`
        """
        return "STOMP CONNECTED Message (version = {0})".format(self.version)


class Send(Message):
    """
    A STOMP ``SEND`` message.
    """

    MESSAGE_TYPE = "SEND"
    """
   The STOMP message code for this type of message.
   """

    def __init__(self, destination, body, receipt = None):
        """

        :param destination: The destination for the message
        :type method: string
        :param body: The text of the message to send.
        :type body: unicode
        :param receipt: The receipt to provide in the message response
        :type method: string
        """
        assert(isinstance(destination, six.string_types))
	assert(type(body) == six.text_type)
        assert(receipt is None or isinstance(receipt, six.string_types))
        Message.__init__(self)
        self.destination = destination
	self.receipt = receipt
	self.body = body

    @staticmethod
    def parse(headers, body):
        """
        Verifies and parses an unserialized raw message into an actual STOMP message instance.
        """
	if 'destination' in headers:
		destination = headers['destination']
	else:
        	raise ProtocolError("missing destination in SEND")
	if 'receipt' in headers:
		receipt = headers['receipt']	
	else:
		receipt = None
        if body is None: 
        	raise ProtocolError("missing body in SEND")
	obj = Send(destination, body, receipt)
        return obj

    def marshal(self):
        """
        Implements :func:`autobahn.stomp.interfaces.IMessage.marshal`
        """
	headers = {'destination' : self.destination}
	if self.receipt is not None:
		headers['receipt'] = self.receipt
        return [Send.MESSAGE_TYPE, headers, self.body]

    def __str__(self):
        """
        Implements :func:`autobahn.stomp.interfaces.IMessage.__str__`
        """
        return "STOMP SEND Message (destination = {0}, receipt={1}, body = {2})".format(self.destination, self.receipt, self.body)

class Error(Message):
    """
    A STOMP ``ERROR`` message.
    """

    MESSAGE_TYPE = "ERROR"
    """
   The STOMP message code for this type of message.
   """

    def __init__(self, message = None, receipt_id = None, body = None):
        """

        :param message: The error message
        :type message: string
	:param receipt_id: The receipt id of the request that caused this error. 
	:type message: unicode
        :param body: Additional error text.
        :type body: unicode
        """
        assert(message is None or isinstance(message, six.string_types))
	assert(receipt_id is None or isinstance(receipt_id, six.string_types))
	assert(body is None or type(body) == six.text_type)
        Message.__init__(self)
        self.message = message
	self.receipt_id = receipt_id;
	self.body = body

    @staticmethod
    def parse(headers, body):
        """
        Verifies and parses an unserialized raw message into an actual STOMP message instance.
        """
	if 'message' in headers:
		message = headers['message']
	else:	
		message = None
	if 'receipt-id' in headers:
		receipt_id = headers['receipt-id']
	else:
		receipt_id = None
	obj = Error(message, receipt_id, body)
        return obj

    def marshal(self):
        """
        Implements :func:`autobahn.stomp.interfaces.IMessage.marshal`
        """
	headers = {}
	if self.message is not None:
		headers['message'] = self.message
	if self.receipt_id is not None:
		headers['receipt-id'] = self.receipt_id
        return [Error.MESSAGE_TYPE, headers, self.body]

    def __str__(self):
        """
        Implements :func:`autobahn.stomp.interfaces.IMessage.__str__`
        """
        return "STOMP Error Message (message = {0}, receipt-id = {1}, body = {2})".format(self.message, self.receipt_id, self.body)

class Receipt(Message):
    """
    A STOMP ``RECEIPT`` message.
    """

    MESSAGE_TYPE = "RECEIPT"
    """
   The STOMP message code for this type of message.
   """

    def __init__(self, receipt_id):
        """
        :param receipt_id: receipt id of the message that has been acknowledged.
        :type reason: unicode
        """
        assert(isinstance(receipt_id, six.string_types))

        Message.__init__(self)
        self.receipt_id = receipt_id 

    @staticmethod
    def parse(headers, body):
        """
        Verifies and parses an unserialized raw message into an actual STOMP message instance.
	"""
	if 'receipt-id' in headers:
		receipt_id = headers['receipt-id']
	else:
        	raise ProtocolError("missing receipt-id in RECEIPT")
        obj = Receipt(receipt_id)
        return obj

    def marshal(self):
        """
        Implements :func:`autobahn.stomp.interfaces.IMessage.marshal`
        """
	headers = {'receipt-id' : self.receipt_id}
        return [Receipt.MESSAGE_TYPE, headers, None]

    def __str__(self):
        """
        Implements :func:`autobahn.stomp.interfaces.IMessage.__str__`
        """
        return "STOMP RECEIPT Message (receipt-id = {0})".format(self.receipt_id)


