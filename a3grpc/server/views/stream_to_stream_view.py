# # -*- coding: utf-8 -*-
# import abc
# import logging
#
# from .view_utils import handle_exception
#
#
# class StreamToStreamView:
#     logger = logging.getLogger(__name__)
#
#     def __init__(self, context, request_iterator):
#         self._context = context
#         self._request_iterator = request_iterator
#
#     def handle_stream_to_stream(self):
#         try:
#             for request in self._request_iterator:
#                 self._handle_request(request)
#                 yield self._handle_reply()
#         except Exception as err:
#             handle_exception(logger=self.logger, context=self._context, err=err)
#
#     @abc.abstractmethod
#     def _handle_request(self, request):
#         raise NotImplementedError()
#
#     @abc.abstractmethod
#     def _handle_reply(self):
#         raise NotImplementedError()
