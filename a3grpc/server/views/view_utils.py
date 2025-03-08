# -*- coding: utf-8 -*-
import logging
import json
import traceback

from a3grpc.patcher import Patcher
from a3exception import errors


def handle_exception(logger: logging.Logger, context, err: Exception):
    if not isinstance(err, errors.Error):
        err = errors.ServerUnknownError(cause=repr(err))

    if err.error_type == errors.ErrorType.ClientSideError:
        code = Patcher.A3StatusCode.ClientSideError
        error_message = f"{code}-[{err.status}]: {err.message}; {err.cause or ''}"
        logger.info(error_message)
    else:
        code = Patcher.A3StatusCode.ServerSideError
        error_message = (
            f"\nstatus: {err.status}\nmessage: {err.message}\ncause: {err.cause}\ntraceback: {traceback.format_exc()}\n"
        )
        logger.critical(error_message)

    details = json.dumps({"status": err.status, "message": err.message}, ensure_ascii=False)
    context.abort(code, details)
