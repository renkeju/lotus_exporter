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

Get lotus environment variables
```
lotus auth-info --perm admin
FULLNODE_API_INFO=asdfghjklqwertyuiopzxcvbnmdqdwewfvde.hlawbdhajkhjksdjhbhchjajdbjbdkjahcvajbajkdlkjLkhkljwhcl.qghjhjbkjvhuiujoi2bf2ufjdnfbajjkhkjkjbcnali:/ip4/127.0.0.1/tcp/1234/http
lotus-miner auth-info --perm admin
MINER_API_INFO=REYTUIBKY78hqckjdkbadsiwbkasvbafodiv.khq2hkjdhqbdhjqyhlufh89jk23njjhbfvHglwlvwjcakjcbiuvjkh2.kjwfbqebfvjh923brj2jef9rkkcjvjevkjoiekjfvnf:/ip4/127.0.0.1/tcp/2345/http
```

use os environments variables

```
export FULLNODE_API_INFO=asdfghjklqwertyuiopzxcvbnmdqdwewfvde.hlawbdhajkhjksdjhbhchjajdbjbdkjahcvajbajkdlkjLkhkljwhcl.qghjhjbkjvhuiujoi2bf2ufjdnfbajjkhkjkjbcnali:/ip4/127.0.0.1/tcp/1234/http
export MINER_API_INFO=REYTUIBKY78hqckjdkbadsiwbkasvbafodiv.khq2hkjdhqbdhjqyhlufh89jk23njjhbfvHglwlvwjcakjcbiuvjkh2.kjwfbqebfvjh923brj2jef9rkkcjvjevkjoiekjfvnf:/ip4/127.0.0.1/tcp/2345/http
python3 main.py --port=9993 --addr=127.0.0.1
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
WorkingDirectory=/opt/lotus_exporter

Environment=FULLNODE_API_INFO=asdfghjklqwertyuiopzxcvbnmdqdwewfvde.hlawbdhajkhjksdjhbhchjajdbjbdkjahcvajbajkdlkjLkhkljwhcl.qghjhjbkjvhuiujoi2bf2ufjdnfbajjkhkjkjbcnali:/ip4/127.0.0.1/tcp/1234/http
Environment=MINER_API_INFO=REYTUIBKY78hqckjdkbadsiwbkasvbafodiv.khq2hkjdhqbdhjqyhlufh89jk23njjhbfvHglwlvwjcakjcbiuvjkh2.kjwfbqebfvjh923brj2jef9rkkcjvjevkjoiekjfvnf:/ip4/127.0.0.1/tcp/2345/http

Type=simple
User=lotus-exp
Group=lotus-exp
ExecStart=python3 main.py --port 9993 --addr 127.0.0.1

SyslogIdentifier=lotus_exporter
Restart=always
RestartSec=1800
StartLimitInterval=0

ProtectHome=yes
NoNewPrivileges=yes

ProtectSystem=strict
ProtectControlGroups=true
```

Create a system user and a system group for lotus_exporter.service

```
groupadd -r lotus-exp
useradd -r -M -g lotus-exp lotus-exp
chown lotus-exp.lotus-exp -R /opt/lotus_exporter
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
    -e MINER_API_INFO=REYTUIBKY78hqckjdkbadsiwbkasvbafodiv.khq2hkjdhqbdhjqyhlufh89jk23njjhbfvHglwlvwjcakjcbiuvjkh2.kjwfbqebfvjh923brj2jef9rkkcjvjevkjoiekjfvnf:/ip4/127.0.0.1/tcp/2345/http \
    -e FULLNODE_API_INFO=asdfghjklqwertyuiopzxcvbnmdqdwewfvde.hlawbdhajkhjksdjhbhchjajdbjbdkjahcvajbajkdlkjLkhkljwhcl.qghjhjbkjvhuiujoi2bf2ufjdnfbajjkhkjkjbcnali:/ip4/127.0.0.1/tcp/1234/http \
    -e DEFAULT_PORT=9993 \
    -e DEFAULT_ADDR=127.0.0.1 \
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
  - [x] Power & Sectors States(Off by default)
  - [x] Sectors Jobs
  - [x] Network
  - [x] Actor Control Wallet Balance
  - [ ] Daels
  - [ ] Daedlines

# Support

![MoyMI Logo](https://raw.githubusercontent.com/renkeju/picture_share/main/moymi-log.png)
