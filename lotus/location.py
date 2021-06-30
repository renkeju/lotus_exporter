#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from geoip2 import database
from netaddr import IPAddress

def ip_location(address):
    split_list = address.split('/')
    ip_address = split_list[2]
    location_dict = {}
    if not IPAddress(ip_address).is_loopback():
        if IPAddress(ip_address).is_unicast() and not IPAddress(ip_address).is_private():
            with database.Reader(os.getcwd() + '/geoip/GeoLite2-City.mmdb') as reader:
                response = reader.city(ip_address)
                location_dict['country_name'] = response.country.name
                location_dict['city_name'] = response.city.name
                location_dict['location_latitude'] = response.location.latitude
                location_dict['location_longitude'] = response.location.longitude
                return location_dict

if __name__ == "__main__":
    print(ip_location('/ip4/61.82.145.85/tcp/46531'))