# -*- coding: utf-8 -*-
"""
Bucket is a small library for building simple web applications. It's inspired
by bottle but has more similar API with FastAPI. Bucket has only single file
with no dependencies other than the Python Standard Library.

Copyright (c) 2025, bagasjs
License: MIT (see the details at the very bottom)
"""

from __future__ import annotations
from typing import Callable

__author__ = 'bagasjs'
__version__ = '0.0.1'
__license__ = 'MIT'

class Request(object):
    pass

class Response(object):
    pass

class Context(object):
    pass

HandlerFunc = Callable[[Context], None]

class Server(object):
    def __init__(self, host='127.0.0.1', port=8080, **options):
        self.options = options
        self.host = host
        self.port = int(port)

    def run(self, handler: HandlerFunc):
        pass

class WSGIServerHandler(object):
    def __init__(self, common_handler: HandlerFunc):
        self.common_handler = common_handler

class CGIServer(Server):
    def run(self, handler: HandlerFunc):
        from wsgiref.simple_server import make_server, WSGIRequestHandler, WSGIServer
        import socket

class WSGIRefServer(Server):
    def run(self, handler: HandlerFunc):
        pass

class GeventServer(Server):
    def run(self, handler: HandlerFunc):
        pass

class Route(object):
    pass

class Router(object):
    pass

class Application(Router):
    def __init__(self):
        super().__init__()

    def handle(self, ctx: Context):
        pass

    def serve(self, host='127.0.0.1', port=8080, **options):
        server = GeventServer(host, port, **options)
        server.run(self.handle)

"""
Copyright (c) 2025 bagasjs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
