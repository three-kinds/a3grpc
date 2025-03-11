# -*- coding: utf-8 -*-
from typing import Iterator
from a3grpc.client import BaseClient

from tests.pb.hello_world_pb2_grpc import GreeterStub
from tests.pb.hello_world_pb2 import HelloReply, HelloRequest


class Client(BaseClient):
    stub_klass = GreeterStub
    _stub: GreeterStub

    def _say_hello(self, name: str) -> str:
        response = self._stub.say_hello(HelloRequest(name=name))
        return response.message

    def say_hello(self, name: str) -> str:
        return self._run_with_retry(self._say_hello, {"name": name})

    def say_stream_hello_reply(self, name_iter: Iterator[str]) -> str:
        pass

    def say_hello_stream_reply(self, name: str) -> Iterator[str]:
        pass

    def say_hello_bidi_stream(self, name_iter: Iterator[str]) -> Iterator[str]:
        pass
