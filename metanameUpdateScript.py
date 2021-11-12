#!/usr/bin/env python3

"""
The purpose of this script is regularly check the public IP of
the router this machine is connected to, then update the domain
record on Metaname's servers accordingly.

Usage: ./metanameUpdateScript.py [-s]
Where:
    -s = silent
"""

from metaname import Client as Metaname
from datetime import datetime
from dotenv import load_dotenv
import subprocess
import sys

# Macros
ENDPOINT = 'https://metaname.nz/api/1.1'
LOGGING = True

"""
Curls a public website to check the public IP address of the machine.
"""
def checkForIPChange(ip_store):
    ip_changed = False
    log('Checking public IP...')
    public_ip = subprocess.check_output(['curl', 'ifconfig.co', '-s']).decode('utf-8').strip()
    try:
        with open(ip_store,'r') as f:
            old_ip = f.readline().strip()
            if public_ip != old_ip:
                ip_changed = True
                log('Old IP: ' + old_ip)
                log('New IP: ' + public_ip)
    except FileNotFoundError:
        log('IP store does not exist', 1)
        log('New IP: ' + str(public_ip))
        ip_changed = True
    return ip_changed, public_ip
"""
Writes an IP address to a local file.
"""
def updateIP(ip_store, new_ip):
    with open(ip_store,'w') as f:
        f.write(new_ip + '\n')
        log('Updated new IP in ./' + ip_store)
"""
Checks DNS entries in the registrar for a given record name.
"""
def checkDNSRecord(metaname, record_name):
    for record in metaname.dns_zone(DOMAIN_NAME):
        if record['name'] == record_name:
            return record
    return {}
"""
Updates a record in the registrar's DNS
"""
def updateDNSRecord(metaname, record_name, new_record):
    record = checkDNSRecord(metaname, record_name)
    try:
        if record['data'] != new_record['data']:
            log('Updating record...')
            metaname.update_dns_record(
                DOMAIN_NAME, 
                record['reference'],
                new_record
            )
            record = checkDNSRecord(metaname, record_name)
            if (record['data'] == new_record['data']):
                log('Record update successful')
        else:
            log('No change in IP between current and suggested record')
    except KeyError:
        log('Can\'t find record matching supplied name', 1)

"""
Simple logging function
"""
def log(msg, severity=0):
    if LOGGING:
        if severity == 0:
            prefix = "LOG"
        elif severity == 1:
            prefix = "ERR"
        logged = "[{0}] [{1}] {2}".format(datetime.now(),prefix,msg)
        print(logged)
        try:
            with open(LOGGING_FILE,'a') as f:
                f.write(logged + '\n')
        except FileNotFoundError:
            with open(LOGGING_FILE, 'w') as f:
                f.write(logged + '\n')

if __name__=='__main__':

    if ('-s' or '--silent') in sys.argv:
        LOGGING = False
    
    # Load vars from .env file
    load_dotenv()

    ACCOUNT_REFERENCE = os.getenv('ACCOUNT_REFERENCE')
    API_KEY = os.getenv('API_KEY')
    RECORD_NAME = os.getenv('RECORD_NAME')
    LOGGING_FILE = os.getenv('LOGGING_FILE')
    IP_STORE_NAME = os.getenv('IP_STORE_NAME')
    DOMAIN_NAME = os.getenv('DOMAIN_NAME')

    ip_changed, public_ip = checkForIPChange(IP_STORE_NAME)

    if ip_changed:
        updateIP(IP_STORE_NAME, public_ip)
        metaname = Metaname(ENDPOINT, ACCOUNT_REFERENCE, API_KEY)
        new_record = {
                'name': RECORD_NAME,
                'type': 'A',
                'ttl': None,
                'data': public_ip
                }
        updateDNSRecord(metaname, RECORD_NAME, new_record)
    else:
        log('No IP change since last execution')
