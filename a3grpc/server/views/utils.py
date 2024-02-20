# -*- coding: utf-8 -*-
import logging
import json
import traceback

from a3exception import errors


def handle_exception(logger: logging.Logger, context, err: Exception):
    if not isinstance(err, errors.Error):
        err = errors.ServerUnknownError(cause=repr(err))

    if err.error_type == errors.ErrorType.ClientSideError:
        code = (400, 'CLIENT_SIDE_ERROR_STATU_SCODE')
        error_message = f'{code}-[{err.status}]: {err.message}; {err.cause or ""}'
        logger.info(error_message)
    else:
        code = (500, 'SERVER_SIDE_ERROR_STATU_SCODE')
        error_message = f"\n" \
                        f"status: {err.status}\n" + \
                        f"message: {err.message}\n" + \
                        f"cause: {err.cause}\n" + \
                        f"traceback: {traceback.format_exc()}\n"
        logger.critical(error_message)

    context.set_code(code)
    context.set_details(json.dumps({
        'status': err.status,
        'message': err.message
    }))
