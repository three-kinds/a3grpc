# -*- coding: utf-8 -*-
import logging
import sys
import os
import signal
from concurrent import futures
import grpc
from a3py.practical.dynamic import import_string
from a3py.practical.signal import PrioritizedSignalHandlerManager, exit_0_handler

from a3grpc.patcher import Patcher


logger = logging.getLogger(__name__)


_example_conf = {
    "host": "127.0.0.1",  # 必须
    "port": "50051",  # 必须
    "max_workers": 1,  # 必须，同时工作的worker数
    "maximum_concurrent_rpcs": 10,  # 必须，维持的链接数
    "servicer_mappings": "app.mappings.servicer_mappings",  # 必须，add_func与Servicer的字典
    "server_key": "/data/ssl/server-key.pem",
    "server_cert": "/data/ssl/server.pem",
    "ca_cert": "/data/ssl/ca.pem",
    "grace_stop_seconds": 10,
    "options": (
        ("grpc.keepalive_time_ms", 10000),
        ("grpc.keepalive_timeout_ms", 5000),
        ("grpc.keepalive_permit_without_calls", True),
        ("grpc.http2.max_pings_without_data", 0),
        ("grpc.http2.min_time_between_pings_ms", 10000),
        ("grpc.http2.min_ping_interval_without_data_ms", 5000),
    ),  # 可选，底层网络连接的细节，当网络不好时配置挺好
    "interceptors": [  # 可选，按需添加配置，类似django的中间件
        "app.interceptors.Interceptor",
    ],
    "patch_status_code": {
        "client_site_error_code": 499,
        "server_site_error_code": 599,
    }
}


def run_grpc_server(conf: dict):
    logger.info("Starting the gRPC service...")

    # patch
    Patcher.patch_status_code(**conf.get("patch_status_code") or dict())

    # preparing Interceptors
    interceptor_list = None
    if isinstance(conf.get("interceptors"), list):
        interceptor_list = list()
        for path in conf["interceptors"]:
            interceptor_klass = import_string(path)
            interceptor_list.append(interceptor_klass())

    # create server
    server = grpc.server(
        thread_pool=futures.ThreadPoolExecutor(max_workers=conf["max_workers"]),
        interceptors=interceptor_list,
        maximum_concurrent_rpcs=conf["maximum_concurrent_rpcs"],
        options=conf.get("options"),
        compression=grpc.Compression.Gzip,
    )
    servicer_mappings = import_string(conf["servicer_mappings"])
    for add_func, servicer in servicer_mappings.items():
        add_func(servicer, server)

    # listen
    host_port = f"{conf['host']}:{conf['port']}"
    server_key = conf.get("server_key")
    server_cert = conf.get("server_cert")
    ca_cert = conf.get("ca_cert")
    if server_key is not None and server_cert is not None and ca_cert is not None:
        private_key = open(server_key, "rb").read()
        cert_chain = open(server_cert, "rb").read()
        root_certificates = open(ca_cert, "rb").read()
        server_credentials = grpc.ssl_server_credentials(
            private_key_certificate_chain_pairs=[(private_key, cert_chain)],
            root_certificates=root_certificates,
            require_client_auth=True,
        )

        listen_result = server.add_secure_port(host_port, server_credentials=server_credentials)
    else:
        listen_result = server.add_insecure_port(host_port)

    # Old versions require manual detection, while new versions will detect automatically.
    if listen_result != int(conf["port"]):
        logger.error(f"Failed to listen on the port: {host_port}.")
        server.stop(0)
        sys.exit(-1)

    server.start()
    logger.info(f"The service has been started: {host_port}，pid: {os.getpid()}")

    # graceful shutdown
    grace_stop_seconds = conf.get("grace_stop_seconds")
    def _graceful_shutdown_handler(*_, **__):
        logger.info(f"Received exit signal, preparing to shut down the service....")
        server.stop(grace=grace_stop_seconds).wait()
        logger.info(f"The gRPC service has been stopped.")

    pm = PrioritizedSignalHandlerManager()
    for sig in [signal.SIGINT, signal.SIGTERM]:
        pm.add_handler(sig, _graceful_shutdown_handler, priority=100)
        pm.add_handler(sig, exit_0_handler, priority=200)

    # block waiting for server termination
    server.wait_for_termination()
