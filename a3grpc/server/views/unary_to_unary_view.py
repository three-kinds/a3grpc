# -*- coding: utf-8 -*-
import abc
import logging
from .utils import handle_exception


class UnaryToUnaryView:
    logger = logging.getLogger(__name__)

    def __init__(self, context, request):
        self._context = context
        self._request = request

    def handle_unary_to_unary(self):
        try:

            return self._handle_request()

        except Exception as err:
            handle_exception(logger=self.logger, context=self._context, err=err)

    @abc.abstractmethod
    def _handle_request(self):
        raise NotImplementedError()
