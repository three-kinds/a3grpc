# -*- coding: utf-8 -*-
from a3grpc.client import BaseClient

from tests.pb.hello_world_pb2_grpc import GreeterStub
from tests.pb.hello_world_pb2 import HelloReply, HelloRequest


class Client(BaseClient):
    stub_klass = GreeterStub
    _stub: GreeterStub

    def _say_hello(self, name: str) -> str:
        response: HelloReply = self._stub.say_hello(HelloRequest(name=name))
        return response.message

    def say_hello(self, name: str) -> str:
        return self._run_with_retry(self._say_hello, {"name": name})
