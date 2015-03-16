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

import six
import re

from autobahn.stomp.interfaces import IObjectSerializer, ISerializer
from autobahn.stomp.exception import ProtocolError
from autobahn.stomp import message

# note: __all__ must be a list here, since we dynamically
# extend it depending on availability of more serializers
__all__ = ['Serializer']


class Serializer:
	"""
    	Class for STOMP serializer. A STOMP serializer is the core glue between
    	parsed STOMP message objects and the bytes on wire (the transport).
    	"""

	LINE_ENDING_REGEX = re.compile('\n|\r\n')

	HEADER_REGEX = re.compile('(?P<key>[^:]+)[:](?P<value>.*)')

	"""
   	Mapping of STOMP message type codes to STOMP message classes.
   	"""

	MESSAGE_TYPE_MAP = {
        	message.STOMP.MESSAGE_TYPE: message.STOMP,
        	message.Connect.MESSAGE_TYPE: message.Connect,
        	message.Connected.MESSAGE_TYPE: message.Connected,
        	message.Send.MESSAGE_TYPE: message.Send
    	}

	def serialize(self, msg):
        	"""
        	Implements :func:`autobahn.stomp.interfaces.ISerializer.serialize`
        	"""
		# ask the message to return its fields
        	[command, headers, body] = msg.serialize()
		# setup a list for each line in the message
        	values = [command]
		# go through each header
        	for key, value in headers.iteritems():
			# create the entry
			value = key + ":" + value
			# append to the end 
			values.append(value) 
		# insert empty line
		values.append("")		
		# if we have a body append it 
		if body is not None:
			values.append(body)
		# convert into a string with each line separated by a line feed with a zero terminator
		frame = "\n".join(values) + '\0';
		# done
		return frame
	

	def unserialize(self, payload, isBinary):
        	"""
        	Implements :func:`autobahn.stomp.interfaces.ISerializer.unserialize`
        	"""

		# only allow text (no binary)
		if isBinary:
                	raise ProtocolError("invalid serialization of STOMP message (binary {0}, but expected {1})".format(isBinary, False))
		
		# split into lines
		lines = LINEEND_REGEX.split(payload)
		# first line is the command
		command = lines.pop(0)

		# decode the class
        	Klass = self.MESSAGE_TYPE_MAP.get(command)
		# make sure this is a command we understand
        	if Klass is None:
			raise ProtocolError("invalid STOMP message type {0}".format(command))

		# parse the headers until we find an empty line
		headers = {}
		while lines[0] != ""
			# get the line
			line = lines.pop(0)
		 	# parse out the header
		        match = HEADER_REGEX.match(line)
			if match is None:
				raise ProtocolError("invalid header line in STOMP message ({0})".format(line))
			# extract the type + value
			key = match.group('key')
			value = match.group('value')
		  	# store as long as it's new
			if not key in headers:
				headers[key] = value	

		# if we reached the last line then there's no body
		body = None
		if len(lines) > 1:
			body = '\n'.join(lines)

        	# this might again raise `ProtocolError` ..
        	msg = Klass.parse(headers, body)

		# done
		return msg

