# a3grpc

To make using gRPC simpler.

[History.](HISTORY.md)

## Install

```shell script
pip install a3grpc

```

## The agreement between the server-side and the client-side

* code 500: ServerSideError, details is json string which contains status and message
* code 400: ClientSideError, details is json string which contains status and message
