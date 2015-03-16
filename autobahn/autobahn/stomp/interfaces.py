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

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class IObjectSerializer(object):
    """
    Raw Python object serialization and deserialization. Object serializers are
    used by classes implementing STOMP serializers, that is instances of
    :class:`autobahn.stomp.interfaces.ISerializer`.
    """

    @abc.abstractmethod
    def serialize(self, obj):
        """
        Serialize an object to a string.

        :param obj: Object to serialize.
        :type obj: Any serializable type.

        :returns: string -- Serialized string.
        """

    @abc.abstractmethod
    def unserialize(self, payload):
        """
        Unserialize objects from a string.

        :param payload: Objects to unserialize.
        :type payload: string

        :returns: list -- List of (raw) objects unserialized.
        """


@six.add_metaclass(abc.ABCMeta)
class IMessage(object):
    """
    A STOMP message.
    """

    @abc.abstractproperty
    def MESSAGE_TYPE(self):
        """
        STOMP message type code.
        """

    @abc.abstractmethod
    def marshal(self):
        """
        Marshal this object into a raw message for subsequent serialization to bytes.

        :returns: list -- The serialized raw message.
        """

    # @abc.abstractstaticmethod ## FIXME: this is Python 3 only
    # noinspection PyMethodParameters
    def parse(headers, body):
        """
        Factory method that parses a unserialized raw message (as returned byte
        :func:`autobahn.interfaces.ISerializer.unserialize`) into an instance
        of this class.

        :returns: obj -- An instance of this class.
        """

    @abc.abstractmethod
    def serialize(self, serializer):
        """
        Serialize this object into a wire level bytes representation and cache
        the resulting bytes. If the cache already contains an entry for the given
        serializer, return the cached representation directly.

        :param serializer: The wire level serializer to use.
        :type serializer: An instance that implements :class:`autobahn.interfaces.ISerializer`

        :returns: bytes -- The serialized bytes.
        """

    @abc.abstractmethod
    def uncache(self):
        """
        Resets the serialization cache.
        """

    @abc.abstractmethod
    def __eq__(self, other):
        """
        Message equality. This does an attribute-wise comparison (but skips attributes
        that start with `_`).
        """

    @abc.abstractmethod
    def __ne__(self, other):
        """
        Message inequality (just the negate of message equality).
        """

    @abc.abstractmethod
    def __str__(self):
        """
        Returns text representation of this message.

        :returns: str -- Human readable representation (e.g. for logging or debugging purposes).
        """


@six.add_metaclass(abc.ABCMeta)
class ISerializer(object):
    """
    STOMP message serialization and deserialization.
    """

    @abc.abstractproperty
    def MESSAGE_TYPE_MAP(self):
        """
        Mapping of STOMP message type codes to STOMP message classes.
        """

    @abc.abstractproperty
    def SERIALIZER_ID(self):
        """
        The STOMP serialization format ID.
        """

    @abc.abstractmethod
    def serialize(self, message):
        """
        Serializes a STOMP message to bytes to be sent to a transport.

        :param message: An instance that implements :class:`autobahn.stomp.interfaces.IMessage`
        :type message: obj

        :returns: tuple -- A pair ``(bytes, isBinary)``.
        """

    @abc.abstractmethod
    def unserialize(self, payload, isBinary):
        """
        Deserialize bytes from a transport and parse into STOMP messages.

        :param payload: Byte string from wire.
        :type payload: bytes

        :returns: list -- List of objects that implement :class:`autobahn.stomp.interfaces.IMessage`.
        """

@six.add_metaclass(abc.ABCMeta)
class ITransport(object):
    """
    A STOMP transport is a bidirectional, full-duplex, reliable, ordered,
    message-based channel.
    """

    @abc.abstractmethod
    def send(self, message):
        """
        Send a STOMP message over the transport to the peer. If the transport is
        not open, this raises :class:`autobahn.stomp.exception.TransportLost`.

        :param message: An instance that implements :class:`autobahn.stomp.interfaces.IMessage`
        :type message: obj
        """

    @abc.abstractmethod
    def isOpen(self):
        """
        Check if the transport is open for messaging.

        :returns: bool -- ``True``, if the transport is open.
        """

    @abc.abstractmethod
    def close(self):
        """
        Close the transport regularly. The transport will perform any
        closing handshake if applicable. This should be used for any
        application initiated closing.
        """

    @abc.abstractmethod
    def abort(self):
        """
        Abort the transport abruptly. The transport will be destroyed as
        fast as possible, and without playing nice to the peer. This should
        only be used in case of fatal errors, protocol violations or possible
        detected attacks.
        """


@six.add_metaclass(abc.ABCMeta)
class ITransportHandler(object):

    @abc.abstractmethod
    def onOpen(self, transport):
        """
        Callback fired when transport is open.

        :param transport: An instance that implements :class:`autobahn.stomp.interfaces.ITransport`
        :type transport: obj
        """

    @abc.abstractmethod
    def onMessage(self, message):
        """
        Callback fired when a STOMP message was received.

        :param message: An instance that implements :class:`autobahn.stomp.interfaces.IMessage`
        :type message: obj
        """

    @abc.abstractmethod
    def onClose(self, wasClean):
        """
        Callback fired when the transport has been closed.

        :param wasClean: Indicates if the transport has been closed regularly.
        :type wasClean: bool
        """


@six.add_metaclass(abc.ABCMeta)
class ISession(object):
    """
    Base interface for STOMP sessions.
    """

    @abc.abstractmethod
    def onConnect(self):
        """
        Callback fired when the transport this session will run over has been established.
        """

    @abc.abstractmethod
    def attach(self):
        """
        Initiate the STOMP connection procedure. 
        """

    @abc.abstractmethod
    def onAttach(self):
        """
        Callback fired when STOMP session has been established.
        """

    @abc.abstractmethod
    def detach(self):
        """
        Actively close this STOMP session.
        """

    @abc.abstractmethod
    def onDetach(self):
        """
        Callback fired when STOMP session has closed
        """

    @abc.abstractmethod
    def disconnect(self):
        """
        Close the underlying transport.
        """

    @abc.abstractmethod
    def onDisconnect(self):
        """
        Callback fired when underlying transport has been closed.
        """

class ISender(ISession):
    """
    Interface for sending STOMP 'SEND' messages to a destination
    """

    @abc.abstractmethod
    def send(self, destination, payload):
        """
        This will return a Deferred/Future, that when resolved, indicates the message
        was accepted by the server.

        - If the send fails, the returned Deferred/Future will be rejected with an instance
          of :class:`autobahn.stomp.exception.ApplicationError`.

        The send may be canceled by canceling the returned Deferred/Future.

        :param destination: The destination for the message.
        :type procedure: unicode

        :param payload: The payload for the message.
        :type procedure: unicode

        :returns: A Deferred/Future for the call result -
        :rtype: instance of :tx:`twisted.internet.defer.Deferred` / :py:class:`asyncio.Future`
        """
