# -*- coding: utf-8 -*-
import grpc
from a3py.improved.json import fast_dumps
from a3grpc.patcher import Patcher


def _unary_unary_rpc_terminator(code, details):
    def terminate(ignored_request, context):
        context.abort(code, details)

    return grpc.unary_unary_rpc_method_handler(terminate)


class ServerInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        if "Bearer" in handler_call_details.invocation_metadata:
            return continuation(handler_call_details)
        else:
            return _unary_unary_rpc_terminator(
                Patcher.A3StatusCode.ClientSideError,
                fast_dumps({"status": "AuthenticationFailedError", "message": "No valid token provided."}),
            )
