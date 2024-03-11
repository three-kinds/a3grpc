# -*- coding: utf-8 -*-
import logging
import grpc
import time
from typing import Type, Tuple, Optional, Callable, TypeVar

from a3py.improved.json import fast_loads
from a3exception.errors import ErrorType, ClientPanicError
from a3exception.dynamic_error_factory import DynamicErrorFactory
from a3grpc.patches import A3StatusCode


def _load_file(filename: str) -> bytes:
    with open(filename, 'rb') as fd:
        return fd.read()


TypeStub = TypeVar('TypeStub')


class BaseClient:
    logger = logging.getLogger(__name__)
    stub_klass: Type[TypeStub] = None

    def __init__(
            self,
            host: str,
            port: int,
            client_cert: str = None,
            client_key: str = None,
            ca_cert: str = None,
            grpc_options: Tuple[Tuple[str, any]] = None,
            compression: int = grpc.Compression.Gzip,
            retry_times: int = 5,
            retry_sleep_seconds: int = 3
    ):
        self._host = host
        self._port = port
        self._client_cert = client_cert
        self._client_key = client_key
        self._ca_cert = ca_cert
        self._grpc_options = grpc_options
        self._compression = compression

        self._retry_times = retry_times
        self._retry_sleep_seconds = retry_sleep_seconds

        self._grpc_channel: Optional[grpc.Channel] = None
        self._stub: TypeStub = None

        self._connect_server()

    def _connect_server(self):
        if None not in {self._client_key, self._client_cert, self._ca_cert}:
            creds = grpc.ssl_channel_credentials(
                root_certificates=_load_file(self._ca_cert),
                private_key=_load_file(self._client_key),
                certificate_chain=_load_file(self._client_cert),
            )
            self._grpc_channel = grpc.secure_channel(
                f'{self._host}:{self._port}',
                creds,
                options=self._grpc_options,
                compression=self._compression
            )
        else:
            self._grpc_channel = grpc.insecure_channel(
                f"{self._host}:{self._port}",
                options=self._grpc_options,
                compression=self._compression
            )

        self._stub = self.stub_klass(self._grpc_channel)

    def _run_with_retry(self, func: Callable, kwargs: dict) -> any:
        status_code = None
        error_message = ""
        for i in range(self._retry_times):
            try:
                return func(**kwargs)
            except grpc.RpcError as e:
                e: grpc.Call
                status_code = e.code()
                error_message = e.details()

                if status_code in [A3StatusCode.ClientSideError, A3StatusCode.ServerSideError]:
                    rd = fast_loads(error_message)
                    if status_code == A3StatusCode.ClientSideError:
                        error_type = ErrorType.ClientSideError
                    else:
                        error_type = ErrorType.ServerSideError

                    rd['error_type'] = error_type
                    raise DynamicErrorFactory.build_error_by_status(**rd)
                else:
                    self.logger.warning(f"[grpc-unexpected-error]: {status_code}, {error_message}, 准备重试")
                    if i + 1 >= self._retry_times:
                        break

                    time.sleep(self._retry_sleep_seconds)
                    if status_code == grpc.StatusCode.UNAVAILABLE:
                        self._connect_server()

        raise ClientPanicError(message=f"服务端不可用，已重试{self._retry_times}，仍无法连接：{status_code}, {error_message}")
