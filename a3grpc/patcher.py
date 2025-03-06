# -*- coding: utf-8 -*-
import enum
from a3py.practical.singleton_meta import SingletonMeta


class Patcher(metaclass=SingletonMeta):
    is_patched = False

    def __init__(
        self,
        unset_error_code: int = 490,
        client_site_error_code: int = 499,
        server_site_error_code: int = 599,
    ):
        self._unset_error_code = unset_error_code
        self._client_site_error_code = client_site_error_code
        self._server_site_error_code = server_site_error_code

        @enum.unique
        class StatusCodeEnum(enum.Enum):
            UnsetError = (self._unset_error_code, "unset error")
            ClientSideError = (self._client_site_error_code, "client side error")
            ServerSideError = (self._server_site_error_code, "server side error")

        self.status_code_enum = StatusCodeEnum

        self._patch_all()

    def _patch_all(self):
        if self.is_patched:
            return

        self.is_patched = True
        self._patch_status_code()

    def _patch_status_code(self):
        status_code = {
            self._unset_error_code: self.status_code_enum.UnsetError,
            self._client_site_error_code: self.status_code_enum.ClientSideError,
            self._server_site_error_code: self.status_code_enum.ServerSideError,
        }

        from grpc import _common  # noqa

        _common.CYGRPC_STATUS_CODE_TO_STATUS_CODE.update(status_code)
        _common.STATUS_CODE_TO_CYGRPC_STATUS_CODE.update(
            {v: k for k, v in status_code.items()}
        )
