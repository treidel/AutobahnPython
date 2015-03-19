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
import inspect

from twisted.python import log
from twisted.application import service
from twisted.internet.defer import Deferred, \
    maybeDeferred, \
    DeferredList, \
    inlineCallbacks

from autobahn.stomp import protocol
from autobahn.websocket.protocol import parseWsUrl
from autobahn.twisted.websocket import StompWebSocketClientFactory

__all__ = (
    'FutureMixin',
    'ApplicationSession',
    'ApplicationSessionFactory'
)


class FutureMixin:
    """
    Mixin for Twisted style Futures ("Deferreds").
    """

    @staticmethod
    def _create_future():
        return Deferred()

    @staticmethod
    def _as_future(fun, *args, **kwargs):
        return maybeDeferred(fun, *args, **kwargs)

    @staticmethod
    def _resolve_future(future, value):
        future.callback(value)

    @staticmethod
    def _reject_future(future, value):
        future.errback(value)

    @staticmethod
    def _add_future_callbacks(future, callback, errback):
        return future.addCallbacks(callback, errback)

    @staticmethod
    def _gather_futures(futures, consume_exceptions=True):
        return DeferredList(futures, consumeErrors=consume_exceptions)


class ApplicationSession(FutureMixin, protocol.ApplicationSession):
    """
    STOMP application session for Twisted-based applications.
    """


class ApplicationSessionFactory(FutureMixin, protocol.ApplicationSessionFactory):
    """
    STOMP application session factory for Twisted-based applications.
    """

    session = ApplicationSession
    """
   The application session class this application session factory will use. Defaults to :class:`autobahn.twisted.stomp.ApplicationSession`.
   """
