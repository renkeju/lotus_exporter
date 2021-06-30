#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import getenv
import time
import json
from . import location
from request import get_json
from prometheus_client import Gauge

sealing_jobs = Gauge(
    "lotus_miner_sealing_job",
    "list running jobs",
    [
        'miner_id',
        'sector_task',
        'sector_state',
        'sector_number',
        'sector_from_worker',
        'sector_from_worker_hostname'
    ]
)

version = Gauge(
    'lotus_miner_version',
    'show version',
    [
        'miner_id',
        'version'
    ]
)

sector_size = Gauge(
    'lotus_miner_sector_size',
    'show owner miner sector size',
    ['miner_id']
)

net_peers = Gauge(
    'lotus_miner_net_peers',
    'Print peers',
    [
        "miner_id",
        "id",
        "address"
    ]
)

net_bandwidth = Gauge(
    'lotus_miner_net_bandwidth',
    'Print bandwidth usage information',
    [
        'miner_id',
        'stats'
    ]
)

sectors_states_count = Gauge(
    'lotus_miner_sectors_states_count',
    'Print sector state count',
    [
        "miner_id",
        "state"
    ]
)

list_all_deals = Gauge(
    'lotus_miner_list_all_deals',
    'List all deals for this miner',
    [
        "miner_id",
        "ProposalCid",
        "DealId",
        "State",
        "Client",
        "Size",
        "Price"
    ]
)

class lotus_miner:
    'lotus miner base class'

    WORKER_JOBS_RUNWAIT_STATE = {
        "1+": "assigned",
        "0": "running",
        "-1": "ret-wait",
        "-2": "returned",
        "-3": "ret-done"
    }

    EXIST_SECOTR_STATE_LIST = [
        "Empty",
        "WaitDeals",
        "Packing",
        "GetTicket",
        "PreCommit1",
        "PreCommit2",
        "PreCommitting",
        "PreCommitWait",
        "WaitSeed",
        "Committing",
        "SubmitCommit",
        "CommitWait",
        "FinalizeSector",
        "Proving",
        "FailedUnrecoverable",
        "SealPreCommit1Failed",
        "SealPreCommit2Failed",
        "PreCommitFailed",
        "ComputeProofFailed",
        "CommitFailed",
        "PackingFailed",
        "FinalizeFailed",
        "DealsExpired",
        "RecoverDealIDs",
        "Faulty",
        "FaultReported",
        "FaultedFinal",
        "Terminating",
        "TerminateWait",
        "TerminateFinality",
        "TerminateFailed",
        "Removing",
        "RemoveFailed",
        "Removed"
    ]

    SECTORS_STATES_VERSION = 0

    SECTORS_STATES_DICT = {
        "Version": SECTORS_STATES_VERSION
    }

    def __init__(self, api, token):
        self.api = api
        self.token = token

        # with open('.sector_states.tmp.json', 'w') as json_file_handler:
        #     json_file_handler.\
        #         write(json.dumps(self.SECTORS_STATES_DICT, indent = 4))

    def miner_id(self):
        actor_address = get_json(self.api, self.token, "ActorAddress", [])
        return actor_address['result']

    def version(self):
        miner_version = get_json(self.api, self.token, 'Version', [])
        version.labels(
            miner_id = self.miner_id(),
            version = miner_version['result']['Version']
        ).set(1)

    def actor_sector_size(self):
        miner_sector_size = \
            get_json(self.api, self.token, "ActorSectorSize", [self.miner_id()])
        sector_size.\
            labels(miner_id=self.miner_id()).set(miner_sector_size['result'])

    def list_running_jobs(self):
        sealing_jobs._metrics.clear()
        running_jobs = get_json(self.api, self.token, "WorkerJobs", [])
        worker_stats = get_json(self.api, self.token, "WorkerStats", [])
        for worker in running_jobs['result']:
            for job in running_jobs['result'][worker]:
                sector_number = job['Sector']['Number']
                sector_task = job['Task']
                sector_state = \
                    self.WORKER_JOBS_RUNWAIT_STATE[str(job['RunWait'])]
                sector_start_time = time.mktime\
                    (time.strptime(job['Start'][:19], '%Y-%m-%dT%H:%M:%S'))
                sector_from_worker = worker
                try:
                    sector_from_worker_hostname = \
                        worker_stats["result"][worker]["Info"]["Hostname"]
                except:
                    sector_from_worker_hostname = "unknown"
                sealing_jobs.labels(
                    miner_id = self.miner_id(),
                    sector_number = sector_number,
                    sector_from_worker = sector_from_worker,
                    sector_from_worker_hostname = sector_from_worker_hostname,
                    sector_task = sector_task,
                    sector_state = sector_state
                ).set(time.time() - sector_start_time)

    def net_peers_list(self):
        net_peers._metrics.clear()
        net_peers_list = get_json(self.api, self.token, 'NetPeers', [])
        for net_peer in net_peers_list['result']:
            net_peer_id = net_peer['ID']
            for index, net_address in enumerate(net_peer['Addrs']):
                net_peers.labels(
                    miner_id = self.miner_id(),
                    id = net_peer_id,
                    address = net_address
                ).set(index+1)

    def net_bandwidth(self):
        net_bandwidth_stats = \
            get_json(self.api, self.token, 'NetBandwidthStats', [])
        net_bandwidth.labels(
            miner_id = self.miner_id(),
            stats = 'TotalIn'
        ).set(net_bandwidth_stats['result']['TotalIn'])
        net_bandwidth.labels(
            miner_id = self.miner_id(),
            stats = 'TotalOut'
        ).set(net_bandwidth_stats['result']['TotalOut'])
        net_bandwidth.labels(
            miner_id = self.miner_id(),
            stats = 'RateIn'
        ).set(net_bandwidth_stats['result']['RateIn'])
        net_bandwidth.labels(
            miner_id = self.miner_id(),
            stats = 'RateOut'
        ).set(net_bandwidth_stats['result']['RateOut'])

    def sectors_list_states(self, count):
        sectors_states_dict = {}
        with open('.sector_states.tmp.json', 'r', encoding='UTF-8') \
            as json_file_handler:
            data = json.load(json_file_handler)
        if data['Version'] == 0:
            for sector_state in self.EXIST_SECOTR_STATE_LIST:
                sectors_state = get_json(
                    self.api, 
                    self.token, 
                    "SectorsListInStates", 
                    [[sector_state]]
                )
                if sectors_state['result'] != None:
                    sectors_state_list_len = len(sectors_state['result'])
                    sectors_states_dict[sector_state] = sectors_state_list_len
            self.SECTORS_STATES_VERSION += 1
            sectors_states_dict_new = {
                'Version': self.SECTORS_STATES_VERSION,
                'result': sectors_states_dict
            }
            with open('.sector_states.tmp.json', 'w') as json_file_handler:
                json_file_handler.\
                    write(json.dumps(sectors_states_dict_new, indent = 4))
        elif data['Version'] in range(1, count):
            with open('.sector_states.tmp.json', 'r') as json_file_handler:
                data = json.load(json_file_handler)
                sectors_states_dict = data['result']
            self.SECTORS_STATES_VERSION += 1
            sectors_states_dict_new = {
                'Version': self.SECTORS_STATES_VERSION,
                'result': sectors_states_dict
            }
            with open('.sector_states.tmp.json', 'w') as json_file_handler:
                json_file_handler.\
                    write(json.dumps(sectors_states_dict_new, indent = 4))
        else:
            self.SECTORS_STATES_VERSION = 0
            sectors_states_dict = {
                'Version': self.SECTORS_STATES_VERSION
            }
            with open('.sector_states.tmp.json', 'w') as json_file_handler:
                json_file_handler.\
                    write(json.dumps(sectors_states_dict, indent = 4))
        for key, value in sectors_states_dict.items():
            sectors_states_count.labels(
                miner_id = self.miner_id(),
                state = key
            ).set(int(value))

    # def storage_deals_list(self):
    #     state_marker_deals = \
    #         get_json(self.api, self.token, "StateMarketDeals", [[]])

    def run(self):
        # self.sectors_list_states(30)
        self.version()
        self.list_running_jobs()
        self.net_peers_list()
        self.net_bandwidth()
        self.actor_sector_size()

