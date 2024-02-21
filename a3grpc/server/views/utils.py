# -*- coding: utf-8 -*-
import logging
import json
import traceback

from a3grpc.patches import A3StatusCode
from a3exception import errors


def handle_exception(logger: logging.Logger, context, err: Exception):
    if not isinstance(err, errors.Error):
        err = errors.ServerUnknownError(cause=repr(err))

    if err.error_type == errors.ErrorType.ClientSideError:
        code = A3StatusCode.ClientSideError
        error_message = f'{code}-[{err.status}]: {err.message}; {err.cause or ""}'
        logger.info(error_message)
    else:
        code = A3StatusCode.ServerSideError
        error_message = f"\n" \
                        f"status: {err.status}\n" + \
                        f"message: {err.message}\n" + \
                        f"cause: {err.cause}\n" + \
                        f"traceback: {traceback.format_exc()}\n"
        logger.critical(error_message)

    details = json.dumps({
        'status': err.status,
        'message': err.message
    }, ensure_ascii=False)
    context.abort(code, details)
