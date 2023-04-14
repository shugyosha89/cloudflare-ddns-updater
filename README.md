# Cloudflare DDNS Records Updater
Update Cloudflare DDNS records with your public IP address.
Run as a cron job (for example every minute) and when an IP address change is detected the rules specified in `rules.yml` will be updated with your new IP.

## Requirements
* Python 3 (not tested on Python 2)
* Python modules in `requirements.txt`

## Usage
Clone the repository:
```
git clone https://github.com/shugyosha89/cloudflare-ddns-updater.git
```

Copy `.env.example` to `.env` and update `API_TOKEN` to your Cloudflare API token (note: it must have DNS edit permission).
Optionally change the log file location.

Copy `rules.yml.example` to `rules.yml` and fill it with a list of zones (headings) and DNS records (list items) you want to update.

Install the requirements using e.g. `pip install -r requirements.txt`.

Set up a cron job to run `update.py` at regular intervals.
Example: Add the below to `crontab -e` to run every minute:
```
* * * * * python3 /path/to/cloudflare-ddns-updater/update.py
```

## Troubleshooting
To force an IP update, change the contents of `ip.txt`.
