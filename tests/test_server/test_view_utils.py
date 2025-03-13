# -*- coding: utf-8 -*-
import logging
from unittest import TestCase

from a3py.improved.json import fast_loads
from a3exception import errors
from a3grpc.patcher import Patcher
from a3grpc.server.views import view_utils


class TestViewUtils(TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)

    def test__handle_exception(self):
        class MockContext:
            def __init__(self):
                self.code = None
                self.details = None

            def abort(self, code, details: str):
                self.code = code
                self.details = details

        context = MockContext()
        handle_exception = view_utils.handle_exception
        logger = logging.getLogger(__name__)

        # ServerUnknownError
        handle_exception(logger, context, ValueError("test"))
        self.assertEqual(context.code, Patcher.A3StatusCode.ServerSideError)
        rd = fast_loads(context.details)
        self.assertEqual(rd["status"], errors.ServerUnknownError.__name__)

        # ClientSideError
        handle_exception(logger, context, errors.ForbiddenError("test"))
        self.assertEqual(context.code, Patcher.A3StatusCode.ClientSideError)
        rd = fast_loads(context.details)
        self.assertEqual(rd["status"], errors.ForbiddenError.__name__)

