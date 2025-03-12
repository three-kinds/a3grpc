# -*- coding: utf-8 -*-
import logging
import multiprocessing
import os
import signal
import sys
import time
import unittest
import socket

from a3grpc.server.start import run_grpc_server, run_grpc_server_with_multiprocessing
from tests.client import Client


class TestServer(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test__run_grpc_server__with_simplest_conf(self):
        class ServerProcess(multiprocessing.Process):
            def run(self):
                conf = {
                    "host": "127.0.0.1",
                    "port": 50051,
                    "max_workers": 10,
                    "maximum_concurrent_rpcs": 100,
                    "servicer_mappings": "tests.server.servicer_mappings",
                }
                run_grpc_server(conf)

        server_process = ServerProcess()
        server_process.start()
        time.sleep(1)

        client = Client(
            host="127.0.0.1",
            port=50051,
        )
        self.assertEqual(client.say_hello("client"), "Hello client!")
        os.kill(server_process.pid, signal.SIGTERM)
        server_process.join()

    def test__run_grpc_server__with_listen_error(self):
        port = 50052
        class SocketProcess(multiprocessing.Process):
            def __init__(self, event: multiprocessing.Event, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.event = event

            def run(self):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('127.0.0.1', port))
                sock.listen(1)
                def _shutdown_handler(*_, **__):
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                    sys.exit(0)

                signal.signal(signal.SIGTERM, _shutdown_handler)
                self.event.set()
                sock.accept()

        ready_event = multiprocessing.Event()
        socket_process = SocketProcess(event=ready_event)
        socket_process.start()
        ready_event.wait(3)
        time.sleep(1)

        class ServerProcess(multiprocessing.Process):
            def run(self):
                conf = {
                    "host": "127.0.0.1",
                    "port": port,
                    "max_workers": 10,
                    "maximum_concurrent_rpcs": 100,
                    "servicer_mappings": "tests.server.servicer_mappings",
                }
                run_grpc_server(conf)

        server_process = ServerProcess()
        server_process.start()
        time.sleep(1)

        self.assertEqual(server_process.is_alive(), False)
        server_process.join()
        os.kill(socket_process.pid, signal.SIGTERM)
        socket_process.join()

    def test__run_grpc_server__with_interceptors(self):
        pass

    def test__run_grpc_server__with_cca(self):
        pass

