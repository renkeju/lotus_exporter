# Prometheus Lotus Metrics Exporter

![Docker Image Version (latest by date)](https://img.shields.io/docker/v/renkeju/lotus_exporter)
![Docker Pulls](https://img.shields.io/docker/pulls/renkeju/lotus_exporter)
![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/renkeju/lotus_exporter)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/renkeju/lotus_exporter)

Prometheus exporter for lotus-daemon and lotus-miner metrics.

## Building and running the exporter

### Run locally

```
git clone https://github.com/renkeju/lotus_exporter.git
cd lotus_exporter
```

use command arguments
```
python3 main.py \
    --miner_api http://127.0.0.1:2345/rpc/v0 \
    --miner_token xxxxxxx \
    --daemon_api http://127.0.0.1:1234/rpc/v0 \
    --daemon_token xxxxxxx \
    --port=9993
```

Or use os environments value

```
export MINER_API=http://127.0.0.1:2345/rpc/v0
export MINER_TOKEN=xxxxxxxx
exoprt DAEMON_API=http://127.0.0.1:1234/rpc/v0
export DAEMON_TOKEN=xxxxxxxxx
export DEFAULT_PORT=9993
python3 main.py
```

If there is no error in executing the command locally, you can use the systemd management service.

```
git clone https://github.com/renkeju/lotus_exporter.git
mv lotus_exporter /opt/lotus_exporter
```

Copy the following content and add it to the `lotus_exporter.service` file in the `/etc/systemd/system` directory.

```ini
[Unit]
Description=Prometheus Lotus Exporter
After=network-online.target

[Service]
Type=simple
User=node-exp
Group=node-exp
ExecStart=python3 main.py \
    --miner_api http://127.0.0.1:2345/rpc/v0 \
    --miner_token xxxxxxx \
    --daemon_api http://127.0.0.1:1234/rpc/v0 \
    --daemon_token xxxxxxx \
    --port 9993

SyslogIdentifier=lotus_exporter
Restart=always
RestartSec=1
StartLimitInterval=0

ProtectHome=yes
NoNewPrivileges=yes

ProtectSystem=strict
ProtectControlGroups=true
```

Create a system user and a system group for lotus_exporter.service

```
groupadd -r node-exp
useradd -r -M -U node-exp node-exp 
```

Start service

```
systemctl daemon-reload
systemctl start lotus_exporter.service
```

### Build Docker Image

```
git clone https://github.com/renkeju/lotus_exporter.git
cd lotus_exporter
docker build . -t lotus_exporter:latest
```

Run Docker

```
docker run -d \
    --network=host \
    --rm \
    -e MINER_API=http://127.0.0.1:2345/rpc/v0 \
    -e MINER_TOKEN=xxxxxxxxx \
    -e DAEMON_API=http://127.0.0.1:1234/rpc/v0 \
    -e DAEMON_TOKEN=xxxxxxxxx \
    -e DEFAULT_PORT=9993 \
    -v /etc/localtime:/etc/localtime \
    lotus_exporter:latest
```

> P.S.: It is recommended to use the host network model. This way promethes will be more convenient to obtain data.

## Features

* daemon
  - [x] Chain Sync State
  - [x] BaseFee
  - [x] Network
  - [x] Wallet Balance
  - [x] Local Message Pool Pending
* miner
  - [x] Wallet Balance
  - [x] Power & Sectors States
  - [x] Sectors Jobs
  - [x] Network
  - [x] Actor Control Wallet Balance
  - [ ] Daels
  - [ ] Daedlines

# Support

![3a53f8cc-51c5-4ae0-b061-3075a11279da.png](https://storage.live.com/items/185FDE718F31F535!53570?authkey=31488497)