# a3grpc

[English](README.md) | 简体中文

`a3grpc`是对grpc做了简单的封装，目的是用起来更简单。

## 1. 简介

### 服务端

* 像django一样，一个接口对应一个View，继承基类View、可以通过抛出异常的方式向客户端返回错误信息
* 使用Servicer包含相关的Views
* 书写`servicer_mappings`，像django的`urls`一样，可以配置多个Servicer
* 准备好如下的配置`conf`，调用`run_grpc_server`或`run_grpc_server_with_multiprocessing`启动服务

```python
conf = {
    # 可选，进程数，在使用 run_grpc_server_with_multiprocessing 时有效，若不指定，则为 cpu_count
    "process_count": 3,
    # 必须
    "host": "127.0.0.1",
    # 必须
    "port": 50051,
    # 必须，同时工作的worker数
    "max_workers": 10,
    # 必须，维持的链接数
    "maximum_concurrent_rpcs": 100,
    # 必须，add_func与Servicer的映射
    "servicer_mappings": "app.mappings.servicer_mappings",
    # 可选，SSL证书
    "server_key": "/data/ssl/server-key.pem",
    "server_cert": "/data/ssl/server.pem",
    "ca_cert": "/data/ssl/ca.pem",
    # 可选，优雅关闭时间
    "graceful_shutdown_seconds": 10,
    # 可选，底层配置，详细：https://grpc.github.io/grpc/core/group__grpc__arg__keys.html
    "options": (
        ("grpc.keepalive_time_ms", 10000),
        ("grpc.keepalive_timeout_ms", 5000),
        ("grpc.keepalive_permit_without_calls", True),
        ("grpc.http2.max_pings_without_data", 0),
        ("grpc.http2.min_ping_interval_without_data_ms", 5000),
        ("grpc.max_receive_message_length", 20 * 1024 * 1024),
        ("grpc.max_send_message_length", 20 * 1024 * 1024),
    ),
    # 可选，类似django的中间件
    "interceptors": [
        "app.interceptors.Interceptor",
    ],
    # 可选，自定义状态码
    "patch_status_code": {
        "client_site_error_code": 499,
        "server_site_error_code": 599,
    }
}
```

### 客户端

* 继承`BaseClient`，实现相应的接口 
* 服务端若反而异常，会自动抛出相关异常实例

## 2. 使用

## 安装

```shell
pip install a3grpc

```

## 样例

* [服务端](tests/server.py)
* [客户端](tests/client.py)
