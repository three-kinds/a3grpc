# a3grpc

`a3grpc` is a simple wrapper around grpc to make it easier to use.

## Install

```shell script
pip install a3grpc

```

## The agreement between the server-side and the client-side

* code 500: ServerSideError, details is json string which contains status and message
* code 400: ClientSideError, details is json string which contains status and message
