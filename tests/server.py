# -*- coding: utf-8 -*-
from typing import Iterator
from a3grpc.server.views import UnaryToUnaryView, StreamToUnaryView, StreamToStreamView, UnaryToStreamView

from tests.pb.hello_world_pb2_grpc import GreeterServicer
from tests.pb.hello_world_pb2 import HelloReply, HelloRequest


class SayHelloView(UnaryToUnaryView):

    def _handle_request(self) -> HelloReply:
        pass


class SayStreamHelloReplyView(StreamToUnaryView):

    def _handle_request(self, request):
        pass

    def _handle_reply(self):
        pass


class SayHelloStreamReplyView(UnaryToStreamView):
    def _handle_request(self):
        pass


class SayHelloBidiStream(StreamToStreamView):
    def _handle_request_iterator(self):
        pass

    def _handle_reply_iterator(self):
        pass


class Greeter(GreeterServicer):

    # todo: context type hint
    def say_hello(self, request: HelloRequest, context) -> HelloReply:
        return SayHelloView(request=request, context=context).handle_unary_to_unary()

    def say_stream_hello_reply(self, request_iterator: Iterator[HelloRequest], context) -> HelloReply:
        return SayStreamHelloReplyView(request_iterator=request_iterator, context=context).handle_stream_to_unary()

    def say_hello_stream_reply(self, request: HelloRequest, context) -> Iterator[HelloReply]:
        yield from SayHelloStreamReplyView(request=request, context=context).handle_unary_to_stream()

    def say_hello_bidi_stream(self, request_iterator: Iterator[HelloRequest], context) -> Iterator[HelloReply]:
        yield from SayHelloBidiStream(request_iterator=request_iterator, context=context).handle_stream_to_stream()
