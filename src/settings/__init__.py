from pathlib import Path
import logging
import yaml
import os
import dotenv

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)

# not used in this stub but often useful for finding various files
PROJECT_PATH = Path(__file__).resolve().parents[2]

dotenv_path = PROJECT_PATH / '.env'
dotenv.load_dotenv(dotenv_path)
ENVIRONMENT = os.environ.get('ENV')
logging.info(f'Environment = {ENVIRONMENT}')


def get_redis_host(env):
    if env == 'dev':
        return 'localhost'
    elif env == 'docker':
        return 'redis_service'
    else:
        raise ValueError(
            'ENV variable may either be "dev" or "docker" in .env')


REDIS = get_redis_host(ENVIRONMENT)

DATA_PATH = PROJECT_PATH / "data"

STATIONS_API_URL = "https://api.jcdecaux.com/vls/v1/stations/"


def get_api_keys(secret_name, env):
    if env == 'docker':
        secret_path = f'/run/secrets/{secret_name}'
    elif env == 'dev':
        secret_path = PROJECT_PATH / 'src' / 'settings' / f'{secret_name}.yml'
    else:
        raise ValueError(
            'ENV variable may either be "dev" or "docker" in .env')

    try:
        with open(secret_path, 'r') as secret_file:
            logging.info(f'Loading secrets from {secret_file.name}')
            return yaml.safe_load(secret_file)
    except IOError:
        logging.error('Did not find {secret_path}')
        return None


API_KEYS = get_api_keys('api_keys', ENVIRONMENT)
