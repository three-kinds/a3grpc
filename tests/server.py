# -*- coding: utf-8 -*-
from a3grpc.server.views import UnaryToUnaryView
from a3grpc.type_hints import Context
from a3exception.errors import ServerKnownError

from tests.pb import hello_world_pb2_grpc
from tests.pb.hello_world_pb2 import HelloReply, HelloRequest


class SayHelloView(UnaryToUnaryView):
    def _handle_request(self) -> HelloReply:
        if self._request.name == "error":
            raise ServerKnownError("The name is not allowed.")
        return HelloReply(message=f"Hello {self._request.name}!")


class GreeterServicer(hello_world_pb2_grpc.GreeterServicer):
    def say_hello(self, request: HelloRequest, context: Context) -> HelloReply:
        return SayHelloView(request=request, context=context).handle_unary_to_unary()


servicer_mappings = {
    hello_world_pb2_grpc.add_GreeterServicer_to_server: GreeterServicer(),
}
