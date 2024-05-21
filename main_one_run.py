
import argparse
import logging
from queue import Queue
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
    logger = setup_logger("main", "output/main.logs")
    logger_result_state = setup_logger("result-state", "output/result_state.logs")
    logger_result_dependencies = setup_logger("result-dependencies", "output/result_dependencies.logs")
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
    queue_basic_block_trace_for_mutation = Queue()
    queue_basic_block_trace_for_checker = Queue()



    target_manifest = "java"
    logger.info("main started")

    #input -> output
    spawnRunPuppet = SpawnRunPuppet(logger, queue_mutation, queue_trace, queue_state, main_lock, target_manifest, oneRun=True) # 1: queue_mutation -> queue_trace
    target_catalog = spawnRunPuppet.get_target_catalog()
    target_manifest_graph = ManifestGraph(target_catalog)
    traceHandling = TraceHandling(logger, queue_trace, queue_basic_block_trace_for_mutation, queue_basic_block_trace_for_checker, main_lock, args, oneRun=True)  # 2:   queue_trace -> queue_basic_block_trace
    riskyMutationGeneration = RiskyMutationGeneration(logger, queue_basic_block_trace_for_mutation, queue_mutation, main_lock, args, oneRun=True)  # 3:   queue_basic_block_trace_for_mutation -> queue_mutation
    stateChecker = StateChecker(logger, logger_result_state, queue_state, main_lock, target_manifest_graph, args, oneRun=True)  # 4:     queue_state, manifest_graph -> log
    traceAnalyzer = TraceAnalyzer(logger, logger_result_dependencies, queue_basic_block_trace_for_checker, main_lock, target_manifest_graph, args, oneRun=True)  # 5:     queue_basic_block_trace_for_checker, manifest_graph  -> log



    queue_mutation.put((0,[])) #initialize the pipeline by running a first time without mutation
    spawnRunPuppet.process_mutation_queue()
    #queue_trace.put((1, 'output/java_2024-05-21_14-11-19/1', 'java'))
    traceHandling.process_tracks()
    stateChecker.process_state_queue()
    traceAnalyzer.process_basic_block_trace_queue()

    for i in range(10):
        riskyMutationGeneration.process_basic_block_trace_queue()
        spawnRunPuppet.process_mutation_queue()
        traceHandling.process_tracks()
        stateChecker.process_state_queue()
        traceAnalyzer.process_basic_block_trace_queue()

if __name__ == '__main__':
    main()




