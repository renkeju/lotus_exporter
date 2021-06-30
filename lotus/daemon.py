#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from request import get_json
from prometheus_client import Gauge


version = Gauge(
    'lotus_daemon_version',
    'show version',
    ['version']
)

sync_status = Gauge(
    'lotus_daemon_sync_status',
    'check sync status',
    [
        "worker_id",
        "stage",
        "end_time",
    ]
)

wallet_balance_list = Gauge(
    'lotus_daemon_wallet_balance',
    'List wallet address and balance',
    [
        "wallet_address",
        "is_default",
        "nonce",
        "id_address"
    ]
)

net_pubsub_scores = Gauge(
    'lotus_daemon_net_pubsub_secores',
    'Print peers pubsub scores',
    ['peer_id']
)

net_peers = Gauge(
    'lotus_daemon_net_peers',
    'Print peers',
    [
        "id",
        "address"
    ]
)

net_bandwidth = Gauge(
    'lotus_daemon_net_bandwidth',
    'Print bandwidth usage information',
    ['stats']
)

message_pool_pending_local = Gauge(
    'lotus_daemon_mpool_pending',
    'get pending messages',
    [
        'From',
        'To',
        'nonce',
        'value',
        'gas_limit',
        'gas_fee_cap',
        'gas_premium',
        'method',
        'params',
        'cid',
        'local'
    ]
)

actor_control_list = Gauge(
    'lotus_actor_control_list',
    'Get currently set control addresses',
    [
        'miner_id',
        'name',
        'id',
        'address',
        'use'
    ]
)

chain_sync_height = Gauge(
    'lotus_daemon_chain_height',
    'Chain Height'
)

chain_basefee = Gauge(
    'lotus_daemon_basefee',
    'Show BaseFee',
    [
        'miner_id',
        'height'
    ]
)

miner_balance = Gauge(
    'lotus_miner_balance',
    'show lotus miner balance',
    [
        'miner_id',
        'state'
    ]
)

market_balance = Gauge(
    'lotus_market_balance',
    'show lotus market balance',
    [
        'miner_id',
        'state'
    ]
)

power = Gauge(
    "lotus_power",
    "show lotus Miner Power and Total Power",
    [
        'miner_id',
        'state'
    ]
)

class lotus_daemon:
    'lotus daemon base class'

    SYNC_STATE_STAGE = [
        "StageIdle",
        "StageHeaders",
        "StagePersistHeaders",
        "StageMessages",
        "StageSyncComplete",
        "StageSyncErrored",
        "StageFetchingMessages"
    ]

    METHODS_MINER = [
        "MethodConstructor",
        "Constructor",
        "ControlAddresses",
        "ChangeWorkerAddress",
        "ChangePeerID",
        "SubmitWindowedPoSt",
        "PreCommitSector",
        "ProveCommitSector",
        "ExtendSectorExpiration",
        "TerminateSectors",
        "DeclareFaults",
        "DeclareFaultsRecovered",
        "OnDeferredCronEvent",
        "CheckSectorProven",
        "ApplyRewards",
        "ReportConsensusFault",
        "WithdrawBalance",
        "ConfirmSectorProofsValid",
        "ChangeMultiaddrs",
        "CompactPartitions",
        "CompactSectorNumbers",
        "ConfirmUpdateWorkerKey",
        "RepayDebt",
        "ChangeOwnerAddress",
        "DisputeWindowedPoSt"
    ]

    ACTOR_CONTROL_USE_TYPE = [
        'post',
        'precommit',
        'commit'
    ]

    def __init__(self, api, token):
        self.api = api
        self.token = token

    def __wallet_balance(self, address):
        wallet_balance = \
            get_json(self.api, self.token, "WalletBalance", [address])
        return wallet_balance['result']

    def __account_key(self, id):
        address = get_json(self.api, self.token, "StateAccountKey", [id, []])
        return address['result']

    def __miner_info(self,miner_id):
        miner_info_state = \
            get_json(self.api, self.token, "StateMinerInfo", [miner_id, []])
        return miner_info_state['result']

    def __chain_height(self):
        chain_head = get_json(self.api, self.token, "ChainHead", [])
        return chain_head['result']

    def __read_state(self, miner_id):
        state_read_state = \
            get_json(self.api, self.token, "StateReadState", [miner_id, []])
        return state_read_state['result']

    def version(self):
        daemon_version = get_json(self.api, self.token, 'Version', [])
        version.labels(
            version = daemon_version['result']['Version']
        ).set(1)

    def sync_state(self):
        sync_status._metrics.clear()
        chain_sync_status = get_json(self.api, self.token, 'SyncState', [])
        for chain_sync_state in chain_sync_status['result']['ActiveSyncs']:
            if chain_sync_state['Stage'] == 4:
                sync_status.labels(
                    worker_id = chain_sync_state['WorkerID'],
                    stage = \
                        self.SYNC_STATE_STAGE[int(chain_sync_state['Stage'])],
                    end_time = chain_sync_state['End'][:19]
                ).set(chain_sync_state['Height'])
            else:
                sync_status.labels(
                    worker_id = chain_sync_state['WorkerID'],
                    stage = \
                        self.SYNC_STATE_STAGE[int(chain_sync_state['Stage'])],
                    end_time = \
                        time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()) 
                ).set(chain_sync_state['Height'])

    def wallet_balance(self):
        wallet_balance_list._metrics.clear()
        wallet_list = get_json(self.api, self.token, 'WalletList', [])
        default_wallet = \
            get_json(self.api, self.token, 'WalletDefaultAddress', [])
        for wallet_address in wallet_list['result']:
            wallet_balance = get_json(
                self.api, 
                self.token, 
                'WalletBalance', 
                [wallet_address]
                )
            mpool_get_nonce = get_json(
                self.api, 
                self.token, 
                'MpoolGetNonce', 
                [wallet_address]
                )
            state_lookup_id = get_json(
                self.api, 
                self.token, 
                'StateLookupID', 
                [wallet_address, []]
                )
            if wallet_address == default_wallet['result']:
                is_default = 'true'
            else:
                is_default = 'false'
            wallet_balance_list.labels(
                wallet_address = wallet_address,
                is_default = is_default,
                nonce = mpool_get_nonce['result'],
                id_address = state_lookup_id['result']
            ).set(int(wallet_balance["result"])/1e18)
            
    def net_scores(self):
        net_pubsub_scores._metrics.clear()
        scores = get_json(self.api, self.token, 'NetPubsubScores', [])
        for peer_score in scores['result']:
            net_pubsub_scores.labels(
                peer_id = peer_score['ID']
            ).set(peer_score['Score']['Score'])

    def net_peers_list(self):
        net_peers._metrics.clear()
        net_peers_list = get_json(self.api, self.token, 'NetPeers', [])
        for net_peer in net_peers_list['result']:
            net_peer_id = net_peer['ID']
            for index, net_address in enumerate(net_peer['Addrs']):
                net_peers.labels(
                    id = net_peer_id,
                    address = net_address
                ).set(index+1)

    def net_bandwidth(self):
        net_bandwidth_stats = \
            get_json(self.api, self.token, 'NetBandwidthStats', [])
        net_bandwidth.labels(
            stats = 'TotalIn'
        ).set(net_bandwidth_stats['result']['TotalIn'])
        net_bandwidth.labels(
            stats = 'TotalOut'
        ).set(net_bandwidth_stats['result']['TotalOut'])
        net_bandwidth.labels(
            stats = 'RateIn'
        ).set(net_bandwidth_stats['result']['RateIn'])
        net_bandwidth.labels(
            stats = 'RateOut'
        ).set(net_bandwidth_stats['result']['RateOut'])

    def mpool_pending(self, local=False):
        message_pool_pending_local._metrics.clear()
        wallet_list = get_json(self.api, self.token, 'WalletList', [])
        mpool_pending_messages = get_json(
            self.api, 
            self.token, 
            'MpoolPending', 
            [[]]
            )
        for message in mpool_pending_messages['result']:
            if local:
                if message['Message']['From'] in wallet_list['result']:
                    message_pool_pending_local.labels(
                        To = message['Message']['To'],
                        From = message['Message']['From'],
                        nonce = message['Message']['Nonce'],
                        value = message['Message']['Value'],
                        gas_limit = message['Message']['GasLimit'],
                        gas_fee_cap = message['Message']['GasFeeCap'],
                        gas_premium = message['Message']['GasPremium'],
                        method = \
                            self.METHODS_MINER[message['Message']['Method']],
                        params = message['Message']['Params'],
                        cid = message['CID']['/'],
                        local = True
                    ).set(message['Message']['Version'])
            else:
                if message['Message']['From'] in wallet_list['result']:
                    message_pool_pending_local.labels(
                        To = message['Message']['To'],
                        From = message['Message']['From'],
                        nonce = message['Message']['Nonce'],
                        value = message['Message']['Value'],
                        gas_limit = message['Message']['GasLimit'],
                        gas_fee_cap = message['Message']['GasFeeCap'],
                        gas_premium = message['Message']['GasPremium'],
                        method = \
                            self.METHODS_MINER[message['Message']['Method']],
                        params = message['Message']['Params'],
                        cid = message['CID']['/'],
                        local = True
                    ).set(message['Message']['Version'])
                else:
                    message_pool_pending_local.labels(
                        To = message['Message']['To'],
                        From = message['Message']['From'],
                        nonce = message['Message']['Nonce'],
                        value = message['Message']['Value'],
                        gas_limit = message['Message']['GasLimit'],
                        gas_fee_cap = message['Message']['GasFeeCap'],
                        gas_premium = message['Message']['GasPremium'],
                        method = \
                            self.METHODS_MINER[message['Message']['Method']],
                        params = message['Message']['Params'],
                        cid = message['CID']['/'],
                        local = False
                    ).set(message['Message']['Version'])

    def actor_control_wallet(self, miner_id):
        owner_id = self.__miner_info(miner_id)['Owner']
        worker_id = self.__miner_info(miner_id)['Worker']
        control_ids = self.__miner_info(miner_id)['ControlAddresses']
        actor_control_list.labels(
            miner_id = miner_id,
            name = "owner",
            id = owner_id,
            address = self.__account_key(owner_id),
            use = "other"
        ).set(int(self.__wallet_balance(self.__account_key(owner_id))) / 1e18)
        actor_control_list.labels(
            miner_id = miner_id,
            name = "worker",
            id = worker_id,
            address = self.__account_key(worker_id),
            use = "other"
        ).set(int(self.__wallet_balance(self.__account_key(worker_id))) / 1e18)
        if control_ids is not None:
            for index, control_id in enumerate(control_ids):
                actor_control_list.labels(
                    miner_id = miner_id,
                    name = "control-{index}".format(index=index),
                    id = control_id,
                    address = self.__account_key(control_id),
                    use = self.ACTOR_CONTROL_USE_TYPE[index]
                ).set(int(self.__wallet_balance(self.__account_key(control_id))) \
                    / 1e18)

    def chain_height(self):
        net_chain_height = self.__chain_height()['Height']
        chain_sync_height.set(net_chain_height)

    def basefee(self):
        chain_basefee._metrics.clear()
        net_chain_blocks = self.__chain_height()['Blocks']
        for block in net_chain_blocks:
            block_height = block['Height']
            block_miner_id = block['Miner']
            block_basefee = int(block['ParentBaseFee'])
            chain_basefee.labels(
                miner_id = block_miner_id,
                height = block_height
            ).set(block_basefee)

    def read_miner_state(self, miner_id):
        read_owner_miner_state = self.__read_state(miner_id)
        available_balance = (int(read_owner_miner_state['Balance']) - \
            (
                int(read_owner_miner_state['State']['PreCommitDeposits']) + \
                int(read_owner_miner_state['State']['InitialPledge']) + \
                int(read_owner_miner_state['State']['LockedFunds'])
            )) / 1e18
        miner_balance.labels(
            miner_id = miner_id,
            state = 'Balance'
        ).set(int(read_owner_miner_state['Balance']) / 1e18)
        miner_balance.labels(
            miner_id = miner_id,
            state = 'PreCommit'
        ).set(int(read_owner_miner_state['State']['PreCommitDeposits']) / 1e18)
        miner_balance.labels(
            miner_id = miner_id,
            state = 'Pledge'
        ).set(int(read_owner_miner_state['State']['InitialPledge']) / 1e18)
        miner_balance.labels(
            miner_id = miner_id,
            state = 'Vesting'
        ).set(int(read_owner_miner_state['State']['LockedFunds']) /1e18)
        miner_balance.labels(
            miner_id = miner_id,
            state = 'Available'
        ).set(available_balance)

    def market_balance(self, miner_id):
        state_market_balance = get_json(
            self.api, 
            self.token, 
            "StateMarketBalance", 
            [miner_id, []]
            )
        market_balance.labels(
            miner_id = miner_id,
            state = "Balance"
        ).set(int(state_market_balance['result']['Escrow']) / 1e18)
        market_balance.labels(
            miner_id = miner_id,
            state = "Locked"
        ).set(int(state_market_balance['result']['Locked']) / 1e18)
        market_balance.labels(
            miner_id = miner_id,
            state = "Available"
        ).set((int(state_market_balance['result']['Escrow']) \
            - int(state_market_balance['result']['Locked'])) / 1e18)

    def state_miner_power(self, miner_id):
        miner_power = get_json(
            self.api, 
            self.token, 
            "StateMinerPower", 
            [miner_id, []]
            )
        power.labels(
            miner_id = miner_id,
            state = "Miner Raw Byte Power"
        ).set(miner_power['result']['MinerPower']['RawBytePower'])
        power.labels(
            miner_id = miner_id,
            state = "Miner Quality Adj Power"
        ).set(miner_power['result']['MinerPower']['QualityAdjPower'])
        power.labels(
            miner_id = miner_id,
            state = "Total Raw Byte Power"
        ).set(miner_power['result']['TotalPower']['RawBytePower'])
        power.labels(
            miner_id = miner_id,
            state = "Total Quality Adj Power"
        ).set(miner_power['result']['TotalPower']['QualityAdjPower'])

    def run(self):
        self.version()
        self.sync_state()
        self.wallet_balance()
        self.net_bandwidth()
        self.net_peers_list()
        self.net_bandwidth()
        self.chain_height()
        self.basefee()
        self.mpool_pending(local=True)