
import argparse
import logging
from threading import Thread, Lock

from spawn_run_puppet import Spawn_run_puppet

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
def setup_logger(name, log_file, level=logging.INFO):
    '''
    To setup as many loggers as you want
    :param name: the name of the logger
    :param log_file: the path to the logs file
    :param level: level of logger
    :return: the logger object
    '''
    try:
        handler = logging.FileHandler(log_file, mode='w')
    except:
        # we launch from main folder
        path = log_file.removeprefix('../../')
        handler = logging.FileHandler(path, mode='w')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger








class init:
    def __init__(self, logger, db_clients_lock, manifest_fi):
        self.logger = logger


def main():
    logger = setup_logger("db-module", "./logs/db-module.logs")
    parser = argparse.ArgumentParser(
        prog='eth_asf_proj',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('-m', '--manifest_file', help='The exact path from the root of the project to the puppet manifest')
    args = parser.parse_args()
    main_lock = Lock()
    


    spawn_run_puppet = Spawn_run_puppet(logger, main_lock, puppet_manifest, args)



    spawn_run_puppet_thread = Thread(target=spawn_run_puppet., args=(comm_info, queue_network, logger,))
    producer.start()
    producer.start()
    producer.start()
    producer.start()
    producer.start()
    producer.start()
    producer.join()
    producer.join()
    producer.join()
    producer.join()
    producer.join()


if __name__ == '__main__':
    main()




