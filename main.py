#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'RenKeju'

import os
import time
import argparse
from typing import Protocol

from prometheus_client import start_http_server
from lotus.daemon import lotus_daemon
from lotus.miner import lotus_miner


__FULLNODE_API_INFO = os.getenv('FULLNODE_API_INFO', 'null')
__MINER_API_INFO = os.getenv('MINER_API_INFO', 'null')

parser = argparse.ArgumentParser(description='Lotus exporter')

if __FULLNODE_API_INFO == 'null':
    parser.add_argument(
        '--fullnode_api_info',
        help = 'Set token with API info required to connect to lotus fullnode',
        required=True
    )

if __MINER_API_INFO == 'null':
    parser.add_argument(
        '--miner_api_info',
        help = 'Set token with API info required to connect to lotus miner',
        required=True
    )

parser.add_argument(
    '--port',
    help = 'Lotus Exporter export port(default: 9993)',
    default=9993
)

parser.add_argument(
    '--addr',
    help = 'Lotus Exporter export address(default: 127.0.0.1)',
    default='127.0.0.1'
)

args = parser.parse_args()

if __FULLNODE_API_INFO == 'null':
    __FULLNODE_API_INFO = args.fullnode_api_info

if __MINER_API_INFO == 'null':
    __MINER_API_INFO = args.miner_api_info

__DEFAULT_PORT = args.port
__DEFAULT_ADDR = args.addr
__FULLNODE_API_INFO_LIST = __FULLNODE_API_INFO.split(':')
__MINER_API_INFO_LIST = __MINER_API_INFO.split(':')
__MINER_API = '{protocol}://{ip_address}:{port}/rpc/v0'.format(
    protocol = __MINER_API_INFO_LIST[1].split('/')[5],
    ip_address = __MINER_API_INFO_LIST[1].split('/')[2],
    port = __MINER_API_INFO_LIST[1].split('/')[4]
)
__MINER_TOKEN = __MINER_API_INFO_LIST[0]
__FULLNODE_API = '{protocol}://{ip_address}:{port}/rpc/v0'.format(
    protocol = __FULLNODE_API_INFO_LIST[1].split('/')[5],
    ip_address = __FULLNODE_API_INFO_LIST[1].split('/')[2],
    port = __FULLNODE_API_INFO_LIST[1].split('/')[4]
)
__FULLNODE_TOKEN = __FULLNODE_API_INFO_LIST[0]

if __name__ == "__main__":
    start_http_server(int(__DEFAULT_PORT), addr=__DEFAULT_ADDR)
    lotus_miner = lotus_miner(api=__MINER_API, token=__MINER_TOKEN)
    lotus_daemon = lotus_daemon(api=__FULLNODE_API, token=__FULLNODE_TOKEN)
    miner_id = lotus_miner.miner_id()
    
    while True:
        lotus_miner.run()
        lotus_daemon.actor_control_wallet(miner_id)
        lotus_daemon.read_miner_state(miner_id)
        lotus_daemon.market_balance(miner_id)
        lotus_daemon.state_miner_power(miner_id)
        lotus_daemon.run()
        time.sleep(30)
