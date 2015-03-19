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

import inspect
import six
from six import StringIO

from autobahn.stomp.interfaces import ITransportHandler
from autobahn.stomp.interfaces import ISession
from autobahn.stomp.interfaces import ISender

from autobahn import util
from autobahn import stomp
from autobahn.stomp import message
from autobahn.stomp import exception
from autobahn.stomp.exception import ProtocolError, SessionNotReady


class Handler:
    """
    """

    def __init__(self, obj, fn, topic, details_arg=None):
        self.obj = obj
        self.fn = fn
        self.topic = topic
        self.details_arg = details_arg


class BaseSession:
    """
    STOMP session base class.

    This class implements :class:`autobahn.stomp.interfaces.ISession`.
    """

    def __init__(self):
        """

        """
        # this is for library level debugging
        self.debug = False

        # this is for app level debugging. exceptions raised in user code
        # will get logged (that is, when invoking remoted procedures or
        # when invoking event handlers)
        self.debug_app = False

        # this is for marshalling traceback from exceptions thrown in user
        # code within STOMP error messages (that is, when invoking remoted
        # procedures)
        self.traceback_app = False

    def onConnect(self):
        """
        Implements :func:`autobahn.stomp.interfaces.ISession.onConnect`
        """

    def onJoin(self, details):
        """
        Implements :func:`autobahn.stomp.interfaces.ISession.onJoin`
        """

    def onDetach(self, details):
        """
        Implements :func:`autobahn.stomp.interfaces.ISession.onDetach`
        """

    def onDisconnect(self):
        """
        Implements :func:`autobahn.stomp.interfaces.ISession.onDisconnect`
        """

    def _message_from_exception(self, exc):
        """
        Create a STOMP error message from an exception.

        :param exc: The exception.
        :type exc: Instance of :class:`Exception` or subclass thereof.
        """
        args = None
        if hasattr(exc, 'args'):
            args = list(exc.args)  # make sure tuples are made into lists

        if isinstance(exc, exception.ApplicationError):
            error = exc.error if type(exc.error) == six.text_type else six.u(exc.error)
        else:
        	error = u"stomp.error.runtime_error"

        msg = message.Error(error, "\n".join(args))

        return msg

    def _exception_from_message(self, msg):
        """
        Create a user (or generic) exception from a STOMP error message.

        :param msg: A STOMP error message.
        :type msg: instance of :class:`autobahn.stomp.message.Error`
        """

        exc = exception.ApplicationError(msg.error)
        return exc


ISession.register(BaseSession)


class ApplicationSession(BaseSession):
    """
    STOMP endpoint session. This class implements

    * :class:`autobahn.stomp.interfaces.ISender`
    * :class:`autobahn.wamp.interfaces.ITransportHandler`
    """

    def __init__(self, host):
        """
        Constructor.
        """
        BaseSession.__init__(self)
	self.host = host

	self._received_connected = False;        
        self._goodbye_sent = False
        self._transport_is_closing = False

        # outstanding requests
        self._send_reqs = {}

    def onOpen(self, transport):
        """
        Implements :func:`autobahn.wamp.interfaces.ITransportHandler.onOpen`
        """
        self._transport = transport
        self.onConnect()

    def onConnect(self):
        """
        Implements :func:`autobahn.stomp.interfaces.ISession.onConnect`
        """
        self.attach()

    def attach(self):
        """
        Implements :func:`autobahn.stomp.interfaces.ISession.attach`
        """
        self._goodbye_sent = False

        msg = message.Connect(self.host)
        self._transport.send(msg)

    def disconnect(self):
        """
        Implements :func:`autobahn.stomp.interfaces.ISession.disconnect`
        """
        if self._transport:
            self._transport.close()
        else:
            raise Exception("transport disconnected")

    def onMessage(self, msg):
        """
        Implements :func:`autobahn.stomp.interfaces.ITransportHandler.onMessage`
        """
        if self._received_connected is False:

            # the first message must be CONNECTED or ERROR
            if isinstance(msg, message.Connected):
                self._received_connected = True
                self._as_future(self.onAttach)

            elif isinstance(msg, message.Error):

                # fire callback and close the transport
                self.onDetach()

            else:
                raise ProtocolError("Received {0} message, and session is not yet established".format(msg.__class__))

        else:

            if isinstance(msg, message.Receipt):
		receipt_id = int(msg.receipt_id)
                if receipt_id in self._send_reqs:

                    d = self._send_reqs.pop(msg.receipt_id)
                    self._resolve_future(d, None)
                else:
                    raise ProtocolError("RECEIPT received for non-pending request ID {0}".format(msg.receipt_id))

            elif isinstance(msg, message.Error):

		# we can only do something if the error is in response to a request we made
		if msg.receipt_id is not None:
			# the deferred for the request that caused the error
                	d = None

                	# ERROR reply to SEND
                	if msg.request in self._send_reqs:
                    		d = self._send_reqs.pop(msg.receipt_id)

                	if d:
                    		self._reject_future(d, self._exception_from_message(msg))
                	else:
	                    	raise ProtocolError("ApplicationSession.onMessage(): ERROR received for non-pending request with receipt-id {0}".format(msg.receipt_id))

            else:
                raise ProtocolError("Unexpected message {0}".format(msg.__class__))

    # noinspection PyUnusedLocal
    def onClose(self, wasClean):
        """
        Implements :func:`autobahn.stomp.interfaces.ITransportHandler.onClose`
        """
        self._transport = None

        if self._received_connected is True:

            # fire callback and close the transport
            try:
                self.onDetach()
            except Exception as e:
                if self.debug:
                    print("exception raised in onDetach callback: {0}".format(e))

            self._received_connected = False

        self.onDisconnect()

    def onAttach(self):
        """
        Implements :func:`autobahn.stomp.interfaces.ISession.onJoin`
        """

    def onDetach(self):
        """
        Implements :func:`autobahn.stomp.interfaces.ISession.onDetach`
        """
        self.disconnect()

    def detach(self):
        """
        Implements :func:`autobahn.stomp.interfaces.ISession.detach`
        """
        if not self._received_connected:
            raise Exception("not attached")

        if not self._goodbye_sent:
            msg = stomp.message.Disconnect()
            self._transport.send(msg)
            self._goodbye_sent = True
        else:
            raise SessionNotReady(u"Already requested to close the session")

    def send(self, destination, payload):
        """
        Implements :func:`autobahn.stomp.interfaces.ISender.send`
        """
        if six.PY2 and type(destination) == str:
            procedure = six.u(destination)
        assert(type(topic) == six.text_type)

        if not self._transport:
            raise exception.TransportLost()

        receipt = util.id()

        msg = message.Send(destination, payload, str(receipt))
        d = self._create_future()
        self._send_reqs[receipt] = d
        self._transport.send(msg)
        return d

ISender.register(ApplicationSession)
ITransportHandler.register(ApplicationSession)

class ApplicationSessionFactory:
    """
    STOMP endpoint session factory.
    """

    session = ApplicationSession
    """
    STOMP application session class to be used in this factory.
    """

    def __init__(self, host):
        """
        Constructor.
        """
	self.host = host


    def __call__(self):
        """
        Creates a new STOMP application session.

        :returns: -- An instance of the STOMP application session class as
                     given by `self.session`.
        """
        session = self.session(self.host)
        session.factory = self
        return session
