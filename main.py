
import argparse
import logging
from multiprocessing import Queue
from threading import Thread, Lock

from manifestGraph import ManifestGraph
from risky_mutation_generation_3 import RiskyMutationGeneration
from run_docker_puppet import SpawnRunPuppet
from state_checker_4 import StateChecker
from trace_analyzer_5 import TraceAnalyzer
from trace_handling_2 import TraceHandling

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

def main():
    logger = setup_logger("db-module", "output/main.logs")
    parser = argparse.ArgumentParser(
        prog='eth_asf_proj',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('-m', '--puppet_manifest', help='The exact path from the root of the project to the puppet manifest')
    args = parser.parse_args()
    main_lock = Lock()

    queue_mutation = Queue()   #elem (idx, elem)
    queue_trace = Queue()
    queue_state = Queue()
    queue_basic_block_trace = Queue()
    queue_mutation = Queue()
    queue_mutation = Queue()


    target_manifest = "java"

    #input -> output
    spawnRunPuppet = SpawnRunPuppet(logger, queue_mutation, queue_trace, main_lock, target_manifest)   #   1:   queue_mutation -> queue_trace
    target_catalog = spawnRunPuppet.get_target_catalog()
    target_manifest_graph = ManifestGraph(target_catalog)
    exit(0)
    traceHandling = TraceHandling(logger, queue_trace, queue_basic_block_trace, main_lock, args)   #   2:   queue_trace -> queue_basic_block_trace
    riskyMutationGeneration = RiskyMutationGeneration(logger, queue_basic_block_trace, queue_mutation, main_lock, args)#   3:   queue_basic_block_trace -> queue_mutation
    stateChecker = StateChecker(logger, queue_state, main_lock, target_manifest_graph, args)  #4:     queue_state, manifest_graph -> log
    traceAnalyzer = TraceAnalyzer(logger, queue_basic_block_trace, main_lock, manifest_graph, args)  #5:     queue_basic_block_trace, manifest_graph  -> log





    spawnRunPuppet_thread = Thread(target=spawnRunPuppet.process_mutation_queue(), args=())
    traceHandling_thread = Thread(target=traceHandling.process_mutation_queue(), args=())
    riskyMutationGeneration_thread = Thread(target=riskyMutationGeneration.process_basic_block_trace_queue(), args=())
    stateChecker_thread = Thread(target=stateChecker.process_state_queue(), args=())
    traceAnalyzer_thread = Thread(target=traceAnalyzer.process_basic_block_trace_queue(), args=())
    spawnRunPuppet_thread.start()
    traceHandling_thread.start()
    riskyMutationGeneration_thread.start()
    stateChecker_thread.start()
    traceAnalyzer_thread.start()
    spawnRunPuppet_thread.join()
    traceHandling_thread.join()
    riskyMutationGeneration_thread.join()
    stateChecker_thread.join()
    traceAnalyzer_thread.join()


if __name__ == '__main__':
    main()




