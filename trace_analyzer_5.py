from manifestGraph import ManifestGraph
class TraceAnalyzer:
    def __init__(self, logger, logger_result, queue_basic_block_trace, main_lock, manifest_graph, args, oneRun=False):
        self.main_lock = main_lock
        self.logger = logger
        self.result_logger = logger
        self.manifest_graph = manifest_graph
        self.args = args
        self.queue_basic_block_trace = queue_basic_block_trace
        self.oneRun = oneRun
        self.logger_result = logger_result





    def process_basic_block_trace_queue(self):
        self.logger.info("TraceAnalyzer : processing started")
        while True:
            block_trace = self.queue_basic_block_trace.get()  # every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            print("process_basic_block_trace_queue")
            self.process_block_trace(block_trace)
            if self.oneRun:
                break

    def process_block_trace(self, trace_temp):
        if trace_temp[1] == RuntimeError:  # The manifest failed to run so no need to test the dependencies
            self.logger_result.info("Run of puppet manifest crash with mutation : ")
            return


        trace_old = trace_temp[1]
        trace = {}
        # this part is responsible for flipping the received dictionary to have each reasource have operations with sets of locations
        # instead of each resource having locations with sets of operations performed on them.
        for i in trace_old:
            trace[i] = {}
            for j in trace_old[i]:
                for k in trace_old[i][j]:
                    if i not in trace or k not in trace[i]:
                        trace[i][k] = {j}
                    else:
                        trace[i][k].add(j)

        #Directy log the result using the result logger
        # list of tuples(lists), these tuples contain pair where the first has to have happened before the second
        before_after = [['accessed', 'remove'], ['write', 'remove'], ['create', 'accessed'], ['create', 'rename'], ['create', 'write'], ['create', 'remove']] # real dependencies
        relations = {}
        # checks if each realation in the list "before_after" is fulfilled for each location
        # that means if one resource creates a file and another resource opens that file, the resource that creates should have happened before
        # so these relations get saved into the "relations" dictionary
        for relation in before_after:
            for i in trace:
                if relation[0] in trace[i]:
                    for j in trace[i][relation[0]]:
                        for k in trace:
                            if relation[1] in trace[k]:
                                if k != i and j in trace[k][relation[1]]:
                                    if i not in relations:
                                        relations[i] = {}
                                    relations[i][k] = 0
        # here we compare these relationships we inferred from the basic block trace to the manifest graph
        missing_dependencies = []
        for i in relations:
            for j in relations[i]:
                if self.manifest_graph.edge_res1_res2(i, j) != "B": # we request to know if in the manifest graph(tree) i has a path to j
                    missing_dependencies.append([i, j]) # if it doesn't, we save it.
        self.logger_result.info("missing dependencies " + str(trace_temp[0]) + ": " + str(missing_dependencies))

