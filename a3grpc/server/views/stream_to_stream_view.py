# -*- coding: utf-8 -*-
import abc
import logging

from .utils import handle_exception


class StreamToStreamView:
    logger = logging.getLogger(__name__)

    def __init__(self, context, request_iterator):
        self._context = context
        self._request_iterator = request_iterator

    def handle_stream_to_stream(self):
        try:

            self._handle_request_iterator()
            yield from self._handle_reply_iterator()

        except Exception as err:
            handle_exception(logger=self.logger, context=self._context, err=err)

    @abc.abstractmethod
    def _handle_request_iterator(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _handle_reply_iterator(self):
        raise NotImplementedError()
