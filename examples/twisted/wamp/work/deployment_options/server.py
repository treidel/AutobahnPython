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

if __name__ == '__main__':

    import sys
    import argparse

    from twisted.python import log
    from twisted.internet.endpoints import serverFromString

    # parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug output.")

    parser.add_argument("-c", "--component", type=str, default=None,
                        help="Start WAMP server with this application component, e.g. 'timeservice.TimeServiceBackend', or None.")

    parser.add_argument("-r", "--realm", type=str, default="realm1",
                        help="The WAMP realm to start the component in (if any).")

    parser.add_argument("--endpoint", type=str, default="tcp:8080",
                        help='Twisted server endpoint descriptor, e.g. "tcp:8080" or "unix:/tmp/mywebsocket".')

    parser.add_argument("--transport", choices=['websocket', 'rawsocket-json', 'rawsocket-msgpack'], default="websocket",
                        help='WAMP transport type')

    args = parser.parse_args()

    # start Twisted logging to stdout
    ##
    if args.debug:
        log.startLogging(sys.stdout)

    # we use an Autobahn utility to install the "best" available Twisted reactor
    ##
    from autobahn.twisted.choosereactor import install_reactor
    reactor = install_reactor()
    if args.debug:
        print("Running on reactor {}".format(reactor))

    # create a WAMP router factory
    ##
    from autobahn.twisted.wamp import RouterFactory
    router_factory = RouterFactory()

    # create a WAMP router session factory
    ##
    from autobahn.twisted.wamp import RouterSessionFactory
    session_factory = RouterSessionFactory(router_factory)

    # if asked to start an embedded application component ..
    ##
    if args.component:
        # dynamically load the application component ..
        ##
        import importlib
        c = args.component.split('.')
        mod, klass = '.'.join(c[:-1]), c[-1]
        app = importlib.import_module(mod)
        SessionKlass = getattr(app, klass)

        # .. and create and add an WAMP application session to
        # run next to the router
        ##
        from autobahn.wamp import types
        session_factory.add(SessionKlass(types.ComponentConfig(realm=args.realm)))

    if args.transport == "websocket":

        # create a WAMP-over-WebSocket transport server factory
        ##
        from autobahn.twisted.websocket import WampWebSocketServerFactory
        transport_factory = WampWebSocketServerFactory(session_factory, debug_wamp=args.debug)
        transport_factory.setProtocolOptions(failByDrop=False)

    elif args.transport in ['rawsocket-json', 'rawsocket-msgpack']:

        # create a WAMP-over-RawSocket transport server factory
        ##
        if args.transport == 'rawsocket-msgpack':
            from autobahn.wamp.serializer import MsgPackSerializer
            serializer = MsgPackSerializer()
        elif args.transport == 'rawsocket-json':
            from autobahn.wamp.serializer import JsonSerializer
            serializer = JsonSerializer()
        else:
            raise Exception("should not arrive here")

        from autobahn.twisted.rawsocket import WampRawSocketServerFactory
        transport_factory = WampRawSocketServerFactory(session_factory, serializer, debug=args.debug)

    else:
        raise Exception("should not arrive here")

    # start the server from an endpoint
    ##
    server = serverFromString(reactor, args.endpoint)
    server.listen(transport_factory)

    # now enter the Twisted reactor loop
    ##
    reactor.run()
