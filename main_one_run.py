
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
from out_put import final_print

def setup_logger(name, log_file, level=logging.INFO):
    '''
    Generic way to setup the logger for the different modules (result, main, info...)
    :param name: the name of the logger
    :param log_file: the path to the logs file
    :param level: level of logger
    :return: the logger object
    '''
    handler = logging.FileHandler(log_file, mode='w')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s') # define each log entry to start by default with the data, time
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def main():
    logger = setup_logger("main", "output/main.logs") # create a logger for avoiding printing to many thing to the terminal
    logger_result_state = setup_logger("result-state", "output/result_state.logs") # create the logger generating the result file for the state comparaison
    logger_result_dependencies = setup_logger("result-dependencies", "output/result_dependencies.logs") # create the logger generating the result file for the depencies checks
    parser = argparse.ArgumentParser(
        prog='eth_asf_proj',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('-tm', '--target_manifest', help='The exact path from the root of the project to the puppet manifest', default="java")
    parser.add_argument('-nr', '--number_run', help='The exact path from the root of the project to the puppet manifest', default=10)
    args = parser.parse_args()
    main_lock = Lock()

    queue_mutation = Queue()   # the different path where each element is of the form  (run idx, data)
    queue_trace = Queue()
    queue_state = Queue()
    queue_basic_block_trace_for_mutation = Queue()
    queue_basic_block_trace_for_checker = Queue()



    target_manifest = args.target_manifest
    nbr_mutation = args.number_run

    logger.info("Main started performing testing on %s manifest for %s iterations" % (target_manifest, nbr_mutation))
    print("Main started performing testing on %s manifest for %s iterations" % (target_manifest, nbr_mutation)) #basic print to see that thing are running

    #input -> output
    spawnRunPuppet = SpawnRunPuppet(logger, logger_result_state, logger_result_dependencies,  queue_mutation, queue_trace, queue_state, main_lock, target_manifest, oneRun=True) # 1: queue_mutation -> queue_trace
    target_catalog = spawnRunPuppet.get_target_catalog() # run the manifest one time on a clean docker image to recover the catalog directly from puppet
    target_manifest_graph = ManifestGraph(target_catalog) # convert the catalog from json to a matrix of relations
    traceHandling = TraceHandling(logger, queue_trace, queue_basic_block_trace_for_mutation, queue_basic_block_trace_for_checker, main_lock, args, oneRun=True)  # 2:   queue_trace -> queue_basic_block_trace
    riskyMutationGeneration = RiskyMutationGeneration(logger, queue_basic_block_trace_for_mutation, queue_mutation, main_lock, args, oneRun=True)  # 3:   queue_basic_block_trace_for_mutation -> queue_mutation
    stateChecker = StateChecker(logger, logger_result_state, queue_state, main_lock, target_manifest_graph, args, oneRun=True)  # 4:     queue_state, manifest_graph -> log
    traceAnalyzer = TraceAnalyzer(logger, logger_result_dependencies, queue_basic_block_trace_for_checker, main_lock, target_manifest_graph, args, oneRun=True)  # 5:     queue_basic_block_trace_for_checker, manifest_graph  -> log


    # First run is without mutation
    queue_mutation.put((0,[])) #initialize the pipeline by running a first time without mutation
    spawnRunPuppet.process_mutation_queue() # spawn a docker puppet image, run the manifest and extract the file hierarchy, strace from it
    traceHandling.process_tracks() # cconvert the strace to a dictionary of resources |-> files |-> action on file
    stateChecker.process_state_queue() # compare state with old run this first call as only as effect to save the state of the run without mutation
    traceAnalyzer.process_basic_block_trace_queue() #analyze the files' action associated to each resource to see if the relations which should exist are present in the catalog/manifest

    for i in range(int(nbr_mutation)):
        riskyMutationGeneration.process_basic_block_trace_queue() # generate mutation on the file with which the manifest interact
        if queue_mutation.qsize()==0: # if already all mutation where processed and no futher where generated stop the execution
            print("FINISHED RUNNING ALL MUTATIONS WITH NO NEW FILES TO EXPLORE")
            break # if all mutation were explored before the max number iteration just stop
        spawnRunPuppet.process_mutation_queue()
        traceHandling.process_tracks()
        stateChecker.process_state_queue()
        traceAnalyzer.process_basic_block_trace_queue()
    print("FINISH RUNNING THE ITERATIONS -> processing the output")
    final_print() # perform the conversion from the result log to a more human centered print, the output is availible in output.txt
    print("OUTPUT SAVED")


if __name__ == '__main__':
    main()