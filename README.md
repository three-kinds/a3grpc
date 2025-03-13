# a3grpc

English | [简体中文](README_ZH.md)

`a3grpc` is a simple wrapper around grpc to make it easier to use.

## 1. Introduction

### Server

* Similar to Django, one API corresponds to one View. Inherit the base class View and return error information to the client by throwing exceptions.
* Use Servicer to contain the relevant Views.
* Write `servicer_mappings`. Similar to Django `urls`, multiple Servicers can be configured.
* Prepare the following configuration `conf` and call `run_grpc_server` or `run_grpc_server_with_multiprocessing` to start the service.

```python
conf = {
    # Optional. Number of processes. It will be used when using run_grpc_server_with_multiprocessing. If not specified, it will be the cpu_count.
    "process_count": 3,
    # Required.
    "host": "127.0.0.1",
    # Required.
    "port": 50051,
    # Required. Number of workers.
    "max_workers": 10,
    # Required. Number of concurrent connections.
    "maximum_concurrent_rpcs": 100,
    # Required. Mapping between add_func and Servicer.
    "servicer_mappings": "app.mappings.servicer_mappings",
    # Optional. SSL certificate.
    "server_key": "/data/ssl/server-key.pem",
    "server_cert": "/data/ssl/server.pem",
    "ca_cert": "/data/ssl/ca.pem",
    # Optional. Graceful shutdown seconds.
    "graceful_shutdown_seconds": 10,
    # Optional. Underlying configuration, details：https://grpc.github.io/grpc/core/group__grpc__arg__keys.html
    "options": (
        ("grpc.keepalive_time_ms", 10000),
        ("grpc.keepalive_timeout_ms", 5000),
        ("grpc.keepalive_permit_without_calls", True),
        ("grpc.http2.max_pings_without_data", 0),
        ("grpc.http2.min_ping_interval_without_data_ms", 5000),
        ("grpc.max_receive_message_length", 20 * 1024 * 1024),
        ("grpc.max_send_message_length", 20 * 1024 * 1024),
    ),
    # Optional. Similar to Django middlewares.
    "interceptors": [
        "app.interceptors.Interceptor",
    ],
    # Optional. Customize the status code.
    "patch_status_code": {
        "client_site_error_code": 499,
        "server_site_error_code": 599,
    }
}
```

### Client

* Inherit `BaseClient` and implement target APIs 
* If the server return an exception, it will automatically throw the exception instance.

## 2. Usage

## Install

```shell
pip install a3grpc

```

## Examples

* [Server](tests/server.py)
* [Client](tests/client.py)
