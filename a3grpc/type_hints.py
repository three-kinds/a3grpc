# -*- coding: utf-8 -*-
from grpc._channel import _InactiveRpcError  # noqa
from google.protobuf import empty_pb2


Empty = empty_pb2.Empty  # noqa
InactiveRpcError = _InactiveRpcError
