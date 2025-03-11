# -*- coding: utf-8 -*-
from typing import Iterator
from a3grpc.server.views import UnaryToUnaryView, StreamToUnaryView, StreamToStreamView, UnaryToStreamView

from tests.pb.hello_world_pb2_grpc import GreeterServicer
from tests.pb.hello_world_pb2 import HelloReply, HelloRequest


class SayHelloView(UnaryToUnaryView):

    def _handle_request(self) -> HelloReply:
        return HelloReply(message=f"Hello {self._request.name}!")


class SayStreamHelloReplyView(StreamToUnaryView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.times = 0

    def _handle_request(self, request: HelloRequest):
        self.times += 1

    def _handle_reply(self) -> HelloReply:
        return HelloReply(message=f"Hello {self.times} times!")


class SayHelloStreamReplyView(UnaryToStreamView):
    def _handle_request(self) -> Iterator[HelloReply]:
        for i in range(3):
            yield HelloReply(message=f"[{i}]Hello {self._request.name}!")


class SayHelloBidiStream(StreamToStreamView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_name = ""

    def _handle_request(self, request: HelloRequest):
        self.current_name = request.name

    def _handle_reply(self) -> HelloReply:
        return HelloReply(message=f"Hello {self.current_name}!")


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
