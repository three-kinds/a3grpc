# -*- coding: utf-8 -*-
from a3grpc.server.views import UnaryToUnaryView
from a3grpc.type_hints import Context

from tests.pb import hello_world_pb2_grpc
from tests.pb.hello_world_pb2 import HelloReply, HelloRequest


class SayHelloView(UnaryToUnaryView):

    def _handle_request(self) -> HelloReply:
        return HelloReply(message=f"Hello {self._request.name}!")


class GreeterServicer(hello_world_pb2_grpc.GreeterServicer):

    def say_hello(self, request: HelloRequest, context: Context) -> HelloReply:
        return SayHelloView(request=request, context=context).handle_unary_to_unary()


servicer_mappings = {
    hello_world_pb2_grpc.add_GreeterServicer_to_server: GreeterServicer(),
}

