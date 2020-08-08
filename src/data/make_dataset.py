# -*- coding: utf-8 -*-
import logging
import fire
import os
import datetime
from src import settings
from manydataapi.velib import DataCollectJCDecaux


def main():
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    stop = datetime.datetime.now() + datetime.timedelta(minutes=2)
    DataCollectJCDecaux.run_collection(os.environ['API_KEY'], contract="marseille",
                                       folder_file=str(
                                           settings.DATA_PATH / "raw"),
                                       delayms=10000, single_file=False, stop_datetime=stop,
                                       log_every=1)
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')


if __name__ == '__main__':
    main()
