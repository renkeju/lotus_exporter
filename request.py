#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' a request module '

__author__ = 'RenKeju'

import sys
import json
import urllib.request
from urllib.parse import urlparse


def get_json(url, token, method, params):
    """standard request api function"""
    jsondata = json.dumps({"jsonrpc": "2.0", "method": "Filecoin." + method, "params": params, "id": 3}).encode("utf8")
    req = urllib.request.Request(url)
    req.add_header('Authorization', 'Bearer ' + token)
    req.add_header("Content-Type", "application/json")

    try:
        response = urllib.request.urlopen(req, jsondata)
    except urllib.error.URLError as e_url:
        print(f'ERROR accessing { url } : { e_url.reason }', file=sys.stderr)
        print(f'DEBUG: method { method } / params { params } ', file=sys.stderr)
        print('lotus_scrape_execution_succeed { } 0')
        sys.exit(0)

    try:
        res = response.read()
        page = res.decode("utf8")

        # parse json object
        obj = json.loads(page)
    except Exception as e_generic:
        print(f'ERROR parsing URL response : { e_generic }', file=sys.stderr)
        print(f'DEBUG: method { method } / params { params } ', file=sys.stderr)
        print(f'DEBUG: { page } ', file=sys.stderr)
        print('lotus_scrape_execution_succeed { } 0')
        sys.exit(0)

    # Check if the answer contain results / otherwize quit
    if "result" not in obj.keys():
        print(f'ERROR { url } returned no result', file=sys.stderr)
        print(f'DEBUG: method { method } / params { params } ', file=sys.stderr)
        print(f'DEBUG: { obj } ', file=sys.stderr)

        # inform the dashboard execution failed
        print('lotus_scrape_execution_succeed { } 0')
        sys.exit(0)

    # output some object attributes
    return obj
