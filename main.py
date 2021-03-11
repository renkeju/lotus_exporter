#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'RenKeju'

import os
import time
import argparse

from prometheus_client import start_http_server
from lotus.daemon import lotus_daemon
from lotus.miner import lotus_miner


__MINER_API = os.getenv('MINER_API', 'null')
__MINER_TOKEN = os.getenv('MINER_TOKEN', 'null')
__DAEMON_API = os.getenv('DAEMON_API', 'null')
__DAEMON_TOKEN = os.getenv('DAEMON_TOKEN', 'null')
__DEFAULT_PORT = os.getenv('DEFAULT_PORT', 'null')

parser = argparse.ArgumentParser(description='Lotus exporter')

if __MINER_API == 'null':
    parser.add_argument(
        '--miner_api',
        help = 'Lotus Miner HTTP RPC-API endpoint\
            (default: "http://127.0.0.1:2345/rpc/v0")',
        default="http://127.0.0.1:2345/rpc/v0",
        required=True
        )

if __MINER_TOKEN == 'null':
    parser.add_argument(
        '--miner_token',
        help='Lotus Miner authorization token',
        required=True
        )

if __DAEMON_API == 'null':
    parser.add_argument(
        '--daemon_api',
        help='Lotus Miner HTTP RPC-API endpoint\
            (default: "http://127.0.0.1:1234/rpc/v0")',
        default="http://127.0.0.1:1234/rpc/v0",
        required=True
        )

if __DAEMON_TOKEN == 'null':
    parser.add_argument(
        '--daemon_token',
        help='Lotus Miner authorization token',
        required=True
        )

if __DEFAULT_PORT == 'null':
    parser.add_argument(
        '--port',
        help='Lotus Exporter export port(default: 9993)',
        default=9993
    )

args = parser.parse_args()

if __MINER_API == 'null':
    __MINER_API = args.miner_api

if __MINER_TOKEN == 'null':
    __MINER_TOKEN = args.miner_token

if __DAEMON_API == 'null':
    __DAEMON_API = args.daemon_api

if __DAEMON_TOKEN == 'null':
    __DAEMON_TOKEN = args.daemon_token

if __DEFAULT_PORT == 'null':
    __DEFAULT_PORT = args.port


if __name__ == "__main__":
    start_http_server(__DEFAULT_PORT)
    lotus_miner = lotus_miner(api=__MINER_API, token=__MINER_TOKEN)
    lotus_daemon = lotus_daemon(api=__DAEMON_API, token=__DAEMON_TOKEN)
    miner_id = lotus_miner.miner_id()
    
    while True:
        lotus_miner.run()
        lotus_daemon.actor_control_wallet(miner_id)
        lotus_daemon.read_miner_state(miner_id)
        lotus_daemon.market_balance(miner_id)
        lotus_daemon.state_miner_power(miner_id)
        lotus_daemon.run()
        time.sleep(30)
