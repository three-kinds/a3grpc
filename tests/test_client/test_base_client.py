# -*- coding: utf-8 -*-
import logging
import multiprocessing
import os
import signal
import time
from unittest import TestCase

from a3grpc.server.start import run_grpc_server
from tests.client import Client


class TestBaseClient(TestCase):

    def test__run_with_retry(self):
        port = 50061
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

        server_process =ServerProcess()
        server_process.start()
        time.sleep(1)

        class ClientProcess(multiprocessing.Process):
            def run(self):
                logging.basicConfig(level=logging.DEBUG)
                client = Client(
                    host="127.0.0.1",
                    port=port,
                    retry_times=2,
                    retry_sleep_seconds=0,
                    patch_status_code={
                        "client_site_error_code": 777,
                        "server_site_error_code": 888
                    }
                )
                client.say_hello("error")

        client_process = ClientProcess()
        client_process.start()
        time.sleep(2)

        self.assertEqual(client_process.is_alive(), False)
        self.assertEqual(client_process.exitcode, 1)
        os.kill(server_process.pid, signal.SIGTERM)
        server_process.join()
