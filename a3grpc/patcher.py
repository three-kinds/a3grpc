# -*- coding: utf-8 -*-
import enum


class _DefaultErrorCode:
    ClientSideError = 499
    ServerSideError = 599


class _ErrorText:
    ClientSideError = "client side error"
    ServerSideError = "server side error"


@enum.unique
class _DefaultA3StatusCode(enum.Enum):
    ClientSideError = (_DefaultErrorCode.ClientSideError, _ErrorText.ClientSideError)
    ServerSideError = (_DefaultErrorCode.ServerSideError, _ErrorText.ServerSideError)


class Patcher:
    has_patched_status_code = False
    A3StatusCode = _DefaultA3StatusCode

    @classmethod
    def patch_status_code(
        cls,
        client_site_error_code: int | None = None,
        server_site_error_code: int | None = None,
    ):
        if cls.has_patched_status_code:
            return

        cls.has_patched_status_code = True

        client_site_error_code = client_site_error_code or _DefaultErrorCode.ClientSideError
        server_site_error_code = server_site_error_code or _DefaultErrorCode.ServerSideError

        if (
            client_site_error_code != _DefaultErrorCode.ClientSideError
            or server_site_error_code != _DefaultErrorCode.ServerSideError
        ):

            @enum.unique
            class A3StatusCode(enum.Enum):
                ClientSideError = (client_site_error_code, _ErrorText.ClientSideError)
                ServerSideError = (server_site_error_code, _ErrorText.ServerSideError)

            cls.A3StatusCode = A3StatusCode

        status_code = {
            client_site_error_code: cls.A3StatusCode.ClientSideError,
            server_site_error_code: cls.A3StatusCode.ServerSideError,
        }

        from grpc import _common  # noqa

        _common.CYGRPC_STATUS_CODE_TO_STATUS_CODE.update(status_code)
        _common.STATUS_CODE_TO_CYGRPC_STATUS_CODE.update({v: k for k, v in status_code.items()})
