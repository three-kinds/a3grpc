# -*- coding: utf-8 -*-
import contextlib
import logging
from pathlib import Path
import os
import signal
import multiprocessing
import socket
from concurrent import futures

import grpc
from a3py.practical.dynamic import import_string
from a3py.practical.signal import PrioritizedSignalHandlerManager, exit_0_handler

from a3grpc.patcher import Patcher

logger = logging.getLogger(__name__)


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
        private_key = Path(server_key).read_bytes()
        cert_chain = Path(server_cert).read_bytes()
        root_certificates = Path(ca_cert).read_bytes()
        server_credentials = grpc.ssl_server_credentials(
            private_key_certificate_chain_pairs=[(private_key, cert_chain)],
            root_certificates=root_certificates,
            require_client_auth=True,
        )
        server.add_secure_port(host_port, server_credentials=server_credentials)
    else:
        server.add_insecure_port(host_port)

    server.start()
    logger.info(f"The service has been started: {host_port}，pid: {os.getpid()}")

    # graceful shutdown
    graceful_shutdown_seconds = conf.get("graceful_shutdown_seconds")

    def _graceful_shutdown_handler(*_, **__):
        logger.info("Received exit signal, preparing to shut down the service....")
        server.stop(grace=graceful_shutdown_seconds).wait()
        logger.info("The gRPC service has been stopped.")

    pm = PrioritizedSignalHandlerManager()
    for signum in [signal.SIGINT, signal.SIGTERM]:
        pm.add_handler(signum, _graceful_shutdown_handler, priority=100)
        pm.add_handler(signum, exit_0_handler, priority=200)

    # block waiting for server termination
    server.wait_for_termination()


@contextlib.contextmanager
def _reserve_port(port: int):
    """Find and reserve a port for all subprocesses to use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 0:
        raise RuntimeError("Failed to set SO_REUSEPORT.")
    sock.bind(("", port))
    try:
        yield sock.getsockname()[1]
    finally:
        sock.close()


def run_grpc_server_with_multiprocessing(conf: dict, process_count: int | None = None):
    process_count = process_count or conf.get("process_count") or multiprocessing.cpu_count()

    with _reserve_port(conf["port"]):
        logger.info(f"{process_count} gRPC processes are being started...")

        worker_list = list()
        for _ in range(process_count):
            worker = multiprocessing.Process(target=run_grpc_server, args=(conf,))
            worker.start()
            worker_list.append(worker)

        def _shutdown_subprocesses(*_, **__):
            logger.info("Received exit signal, preparing to shut down the subprocesses....")
            for w in worker_list:
                os.kill(w.pid, signal.SIGTERM)

        for signum in [signal.SIGINT, signal.SIGTERM]:
            signal.signal(signum, _shutdown_subprocesses)

        for worker in worker_list:
            worker.join()
