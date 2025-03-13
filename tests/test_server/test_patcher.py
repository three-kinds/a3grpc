# -*- coding: utf-8 -*-
from unittest import TestCase

from a3grpc.patcher import Patcher


class TestPatcher(TestCase):

    def test_patch_status_code(self):
        raw_status_code = Patcher.A3StatusCode
        client_site_error_code = 777
        server_site_error_code = 888
        Patcher.patch_status_code(
            client_site_error_code=client_site_error_code,
            server_site_error_code=server_site_error_code
        )
        self.assertEqual(
            Patcher.A3StatusCode.ClientSideError.value[0], client_site_error_code
        )
        self.assertEqual(
            Patcher.A3StatusCode.ServerSideError.value[0], server_site_error_code
        )
        # unchanged
        Patcher.patch_status_code(
            client_site_error_code=client_site_error_code + 1,
            server_site_error_code=server_site_error_code + 1
        )
        self.assertEqual(
            Patcher.A3StatusCode.ClientSideError.value[0], client_site_error_code
        )
        self.assertEqual(
            Patcher.A3StatusCode.ServerSideError.value[0], server_site_error_code
        )
        # restore
        Patcher.has_patched_status_code = False
        Patcher.A3StatusCode = raw_status_code
        Patcher.patch_status_code()
        self.assertNotEqual(
            Patcher.A3StatusCode.ClientSideError.value[0], client_site_error_code
        )
        self.assertNotEqual(
            Patcher.A3StatusCode.ServerSideError.value[0], server_site_error_code
        )
