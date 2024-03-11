# -*- coding: utf-8 -*-
import enum


@enum.unique
class A3StatusCode(enum.Enum):
    ClientSideError = (400, "client side error")
    ServerSideError = (500, "server side error")


# Both the client-side and the server-side must run this patch.
def patch_status_code():
    from grpc import _common # noqa
    a3_status_code = {
        400: A3StatusCode.ClientSideError,
        500: A3StatusCode.ServerSideError,
    }
    _common.CYGRPC_STATUS_CODE_TO_STATUS_CODE.update(a3_status_code)
    _common.STATUS_CODE_TO_CYGRPC_STATUS_CODE.update({v: k for k, v in a3_status_code.items()})
