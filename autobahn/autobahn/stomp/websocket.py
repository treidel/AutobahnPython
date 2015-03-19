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

import traceback

from autobahn.websocket import protocol
from autobahn.websocket import http
from autobahn.stomp.interfaces import ITransport
from autobahn.stomp.serializer import Serializer
from autobahn.stomp.exception import ProtocolError, SerializationError, TransportLost

__all__ = ('StompWebSocketClientProtocol',
           'StompWebSocketClientFactory')


class StompWebSocketProtocol:
	"""
    	Base class for STOMP-over-WebSocket transport mixins.
    	"""

    	def _bailout(self, code, reason=None):
        	self.failConnection(code, reason)

    	def onOpen(self):
        	"""
        	Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onOpen`
        	"""
        	# WebSocket connection established. Now let the user STOMP session factory
        	# create a new STOMP session and fire off session open callback.
        	try:
            		self._session = self.factory._factory()
            		self._session.onOpen(self)
        	except Exception as e:
            		# Exceptions raised in onOpen are fatal ..
            		reason = "STOMP Internal Error ({0})".format(e)
            		self._bailout(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_INTERNAL_ERROR, reason=reason)

	def onClose(self, wasClean, code, reason):
        	"""
        	Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onClose`
        	"""
        	# STOMP session might never have been established in the first place .. guard this!
        	if hasattr(self, '_session') and self._session:
            		# WebSocket connection lost - fire off the STOMP
            		# session close callback
            		# noinspection PyBroadException
            		try:
                		self._session.onClose(wasClean)
            		except Exception:
                		# silently ignore exceptions raised here ..
            			self._session = None

	def onMessage(self, payload, isBinary):
        	"""
        	Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onMessage`
        	"""
        	try:
            		msg = self._serializer.unserialize(payload, isBinary)
                	self._session.onMessage(msg)

		except ProtocolError as e:
            		reason = "STOMP Protocol Error ({0})".format(e)
            		self._bailout(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_PROTOCOL_ERROR, reason=reason)

        	except Exception as e:
            		reason = "STOMP Internal Error ({0})".format(e)
            		self._bailout(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_INTERNAL_ERROR, reason=reason)

    	def send(self, msg):
        	"""
        	Implements :func:`autobahn.stomp.interfaces.ITransport.send`
        	"""
        	if self.isOpen():
            		try:
                		payload = self._serializer.serialize(msg)
            		except Exception as e:
                		# all exceptions raised from above should be serialization errors ..
                		raise SerializationError("Unable to serialize STOMP application payload ({0})".format(e))
                	# send the message
			self.sendMessage(payload.encode(), False)
        	else:
            		raise TransportLost()

    	def isOpen(self):
        	"""
        	Implements :func:`autobahn.stomp.interfaces.ITransport.isOpen`
        	"""
        	return self._session is not None

    	def close(self):
        	"""
        	Implements :func:`autobahn.stomp.interfaces.ITransport.close`
        	"""
        	if self.isOpen():
            		self.sendClose(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_NORMAL)
        	else:
            		raise TransportLost()

    	def abort(self):
        	"""
        	Implements :func:`autobahn.stomp.interfaces.ITransport.abort`
        	"""
        	if self.isOpen():
            		self._bailout(protocol.WebSocketProtocol.CLOSE_STATUS_CODE_GOING_AWAY)
        	else:
            		raise TransportLost()


ITransport.register(StompWebSocketProtocol)

class StompWebSocketClientProtocol(StompWebSocketProtocol):
    	"""
    	Mixin for STOMP-over-WebSocket client transports.
    	"""

    	def onConnect(self, response):
        	"""
        	Callback from :func:`autobahn.websocket.interfaces.IWebSocketChannel.onConnect`
        	"""
		# make sure the protocol is STOMP v1.2 there is no subprotocol for STOMP-over-Websocket
		if response.protocol not in self.factory.protocols:
                	raise Exception("Server does not speak any of the WebSocket subprotocols we requested (%s)." % ', '.join(self.factory.protocols))

		# create the serializer
        	self._serializer = Serializer()

class StompWebSocketFactory:
    """
    Base class for STOMP-over-WebSocket transport factory mixins.
    """

    def __init__(self, factory):
        """
        Ctor.

        :param factory: A callable that produces instances that implement
           :class:`autobahn.stomp.interfaces.ITransportHandler`
        :type factory: callable
        """
        assert(callable(factory))
        self._factory = factory

	# only support v12.stomp for now
	self._protocols = ["v12.stomp"]

class StompWebSocketServerFactory(StompWebSocketFactory):
    """
    Mixin for STOMP-over-WebSocket server transport factories.
    """


class StompWebSocketClientFactory(StompWebSocketFactory):
    """
    Mixin for STOMP-over-WebSocket client transport factories.
    """
