from pathlib import Path
import logging
import os
from dotenv import find_dotenv, load_dotenv


log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)

# not used in this stub but often useful for finding various files
PROJECT_PATH = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_PATH / "data"
# find .env automagically by walking up directories until it's found, then
# load up the .env entries as environment variables
load_dotenv(find_dotenv())
