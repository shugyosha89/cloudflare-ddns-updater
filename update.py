#!/usr/bin/env python3
"""
Script to update Cloudflare DDNS records with the machine's current public IP address.
"""

__author__ = "Matthew Bowen"
__version__ = "0.1.0"
__license__ = "MIT"

from dotenv import load_dotenv
import logging
import logzero
from logzero import logger
import requests
import os
import pathlib
import yaml

SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()

def configure_logging():
    if log_file := os.environ.get('LOG_FILE'):
        logzero.logfile(log_file)
    if log_level := os.environ.get('LOG_LEVEL'):
        logzero.loglevel(logging.getLevelName(log_level.upper()))

def get_zone_id(zone_name):
    url = f'https://api.cloudflare.com/client/v4/zones?name={zone_name}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {os.environ.get('API_TOKEN')}",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['result'][0]['id']

def get_zone_records(zone_id):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {os.environ.get('API_TOKEN')}",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    result = response.json()['result']
    return {record['name']: record for record in result}

def update_record(zone_id, record, ip):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record["id"]}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {os.environ.get('API_TOKEN')}",
    }
    requests.put(url, headers=headers, json={
        'name': record['name'],
        'type': record['type'],
        'content': ip,
        'ttl': record['ttl'],
        'proxied': record['proxied'],
    }).raise_for_status()

def update(ip):
    with open(f'{SCRIPT_DIR}/rules.yml', 'r') as file:
        rules = yaml.safe_load(file)
    for zone, names in rules.items():
        logger.debug(f"Updating zone {zone}")
        try:
            zone_id = get_zone_id(zone)
            records = get_zone_records(zone_id)
            for name in names:
                logger.debug(f"Updating record {name}")
                try:
                    update_record(zone_id, records[name], ip)
                except Exception as e:
                    logger.error(f'Failed to update record {name}: {e}')
        except Exception as e:
            logger.error(f'Failed to update zone {zone}: {e}')

def main():
    ip = requests.get(os.environ.get('IP_SERVER')).text.strip()
    with open(f'{SCRIPT_DIR}/ip.txt', 'r') as f:
        old_ip = f.read().strip()

    if ip == old_ip:
        logger.info('No change')
        exit(0)

    logger.info(f'IP changed from {old_ip} to {ip}')
    with open(f'{SCRIPT_DIR}/ip.txt', 'w') as f:
        f.write(ip)

    update(ip)
    logger.info('Done')

if __name__ == "__main__":
    load_dotenv()
    configure_logging()
    main()
