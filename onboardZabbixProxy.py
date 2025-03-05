#!/usr/bin/env python3.9
import os
import requests
import json
from jsonpath_ng import jsonpath, parse
from pprint import pprint
import urllib3
urllib3.disable_warnings()

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--proxyName',help='Name of the proxy (required)',type=str,required=True)
parser.add_argument('--PSKIdentity',help='PSKIdentity',type=str,required=True)
parser.add_argument('--PSK',help='abcabcabcabcabcabcabcabcabcabcab',type=str,required=True)
parser.add_argument('--LocalAdress',help='IP address for Zabbix proxy. All active agents will point to this.',type=str,required=True)
parser.add_argument('--LocalPort',help='10051',type=str,required=True)
parser.add_argument('--api_jsonrpc',help='https://127.0.0.1:44372/api_jsonrpc.php',type=str,required=True)
parser.add_argument('--token',help='7aad548037e06da49c5f29cfe990355b25ab0bb482565c79cbdb5ef7164fe565',type=str,required=True)

args = parser.parse_args()

proxy = args.proxyName
identity = args.PSKIdentity
psk = args.PSK
ip = args.LocalAdress
port = args.LocalPort
token = args.token
url = args.api_jsonrpc

print(f"Proxy Name: {args.proxyName}")
print(f"Proxy PSK Identity: {args.PSKIdentity}")
print(f"Proxy PSK key: {args.PSK}")

# extract first 3 characters
proxyCodeName = proxy[:3]

print('proxy code name will be: '+ proxyCodeName)

# define token in header
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+token}

# pick up all proxy groups
proxyGroups = parse('$.result').find(json.loads(requests.request("POST", url, headers=headers, data=json.dumps(
    {"jsonrpc":"2.0","method":"proxygroup.get","params":{"output":["proxy_groupid","name"]},"id":1}
    ), verify=False).text))[0].value

proxy_groupid = 0
# if proxy group already exist, then pick up ID
for hagroup in proxyGroups:
    if proxyCodeName == hagroup['name']:
        proxy_groupid = hagroup['proxy_groupid']

# if proxy group does not exist
if proxy_groupid == 0:
    proxyGroupCreate = parse('$.result').find(json.loads(requests.request("POST", url, headers=headers, data=json.dumps(
        {
	"jsonrpc": "2.0",
	"method": "proxygroup.create",
	"params": {
		"name": proxyCodeName,
		"failover_delay": "1m",
		"min_online": "1"
	},
	"id": 1
    }
        ), verify=False).text))[0].value
    print(proxyGroupCreate)
    pprint(proxyGroupCreate)

    proxy_groupid = proxyGroupCreate["proxy_groupids"][0]

print('Proxy groups:');pprint(proxyGroups);print()


# fetch proxy list
proxyList = parse('$.result').find(json.loads(requests.request("POST", url, headers=headers, data=json.dumps(
    {"jsonrpc":"2.0","method":"proxy.get","params":{"output":["proxyid","name"]},"id":1}
    ), verify=False).text))[0].value
print(proxyList)

# validate if proxy is registred
proxyRegistred = 0
for prx in proxyList:
    if proxy == prx['name']:
        proxyRegistred = 1
        break

if not proxyRegistred:
    createProxy = parse('$.result').find(json.loads(requests.request("POST", url, headers=headers, data=json.dumps(
    {
	"jsonrpc": "2.0",
	"method": "proxy.create",
	"params": {
		"name": proxy,
		"local_address": ip,
		"local_port": port,
		"proxy_groupid": proxy_groupid,
		"tls_accept": "2",
		"tls_psk_identity": identity,
		"tls_psk": psk,
		"operating_mode": "0"
	},
	"id": 1
    }
    ), verify=False).text))[0].value
    pprint(createProxy)

