from pathlib import Path
import logging
import os
import yaml

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)

# not used in this stub but often useful for finding various files
PROJECT_PATH = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_PATH / "data"

STATIONS_API_URL = "https://api.jcdecaux.com/vls/v1/stations/"


def get_api_keys(secret_name):
    try:
        with open('/run/secrets/{0}'.format(secret_name), 'r') as secret_file:
            logging.info(f'Loading secrets from {secret_file}')
            return yaml.safe_load(secret_file)
    except IOError:
        logging.error('Did not find /run/secrets/{0}'.format(secret_name))
        return None


API_KEYS = get_api_keys('api_keys')
