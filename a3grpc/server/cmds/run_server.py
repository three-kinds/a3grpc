# -*- coding: utf-8 -*-
import sys
import os
from logging import Logger
from concurrent import futures
import grpc
from a3py.simplified.dynamic import import_string


_example_conf = {
    'host': '127.0.0.1',                                    # 必须
    'port': '50051',                                        # 必须
    'max_workers': 1,                                       # 必须，同时工作的worker数
    'maximum_concurrent_rpcs': 10,                          # 必须，维持的链接数
    'servicer_mappings': 'app.mappings.servicer_mappings',  # 必须，add_func与Servicer的字典
    'server_key': '/data/ssl/server-key.pem',
    'server_cert': '/data/ssl/server.pem',
    'ca_cert': '/data/ssl/ca.pem',
    'options': (
        ('grpc.keepalive_time_ms', 10000),
        ('grpc.keepalive_timeout_ms', 5000),
        ('grpc.keepalive_permit_without_calls', True),
        ('grpc.http2.max_pings_without_data', 0),
        ('grpc.http2.min_time_between_pings_ms', 10000),
        ('grpc.http2.min_ping_interval_without_data_ms', 5000),
    ),                                                       # 可选，底层网络连接的细节，当网络不好时配置挺好
    'interceptors': [                                        # 可选，按需添加配置，类似django的中间件
        'app.interceptors.Interceptor',
    ]
}


def run_grpc_server(conf: dict, logger: Logger):
    logger.info('[BOOT]启动GRPC服务中...')

    # 准备拦截器
    interceptor_list = None
    if isinstance(conf.get('interceptors'), list):
        interceptor_list = list()
        for path in conf['interceptors']:
            interceptor_klass = import_string(path)
            interceptor_list.append(interceptor_klass())

    # 创建服务
    server = grpc.server(
        thread_pool=futures.ThreadPoolExecutor(max_workers=conf['max_workers']),
        interceptors=interceptor_list,
        maximum_concurrent_rpcs=conf['maximum_concurrent_rpcs'],
        options=conf.get('options'),
        compression=grpc.Compression.Gzip
    )

    # 添加service_instance
    servicer_mappings = import_string(conf['servicer_mappings'])
    for add_func, servicer in servicer_mappings.items():
        add_func(servicer, server)

    # 准备监听
    host_port = f"{conf['host']}:{conf['port']}"
    server_key = conf.get('server_key')
    server_cert = conf.get('server_cert')
    ca_cert = conf.get('ca_cert')
    if server_key is not None and server_cert is not None and ca_cert is not None:
        # 准备 ssl
        private_key = open(server_key, 'rb').read()
        cert_chain = open(server_cert, 'rb').read()
        root_certificates = open(ca_cert, 'rb').read()
        server_credentials = grpc.ssl_server_credentials(
            private_key_certificate_chain_pairs=[(private_key, cert_chain)],
            root_certificates=root_certificates,
            require_client_auth=True
        )

        # ssl listen
        listen_result = server.add_secure_port(
            host_port, server_credentials=server_credentials
        )
    else:
        # 普通 listen
        listen_result = server.add_insecure_port(
            host_port
        )

    # 老版本需要手动检测，新版本会自动检测
    if listen_result != int(conf['port']):
        logger.critical(f'[ABORT]端口监听失败: {host_port}')
        server.stop(0)
        sys.exit(-1)

    server.start()
    logger.info(f'[SUCCESS]服务已开启: {host_port}，主进程: {os.getpid()}')
    server.wait_for_termination()
