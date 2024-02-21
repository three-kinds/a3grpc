# -*- coding: utf-8 -*-
import abc
import logging

from .utils import handle_exception


class UnaryToStreamView:
    logger_name = None

    def __init__(self, context, request):
        self._logger = logging.getLogger(self.logger_name)
        self._context = context
        self._request = request

    def handle_unary_to_stream(self):
        try:

            yield from self._handle_request()

        except Exception as err:
            handle_exception(logger=self._logger, context=self._context, err=err)

    @abc.abstractmethod
    def _handle_request(self):
        raise NotImplementedError()
