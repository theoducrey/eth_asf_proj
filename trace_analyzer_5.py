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
            self.process_block_trace(block_trace)
            if self.oneRun:
                break

    def process_block_trace(self, trace_temp):
        trace_old = trace_temp[1]
        trace = {}
        #print(trace_old)
        for i in trace_old:
            trace[i] = {}
            for j in trace_old[i]:
                for k in trace_old[i][j]:
                    if i not in trace or k not in trace[i]:
                        trace[i][k] = {j}
                    else:
                        trace[i][k].add(j)

        #Directy log the result using the result logger
        before_after = [['accessed', 'remove'],["accessed", "accessed"]] # list of tuples(lists), these tuples contain pair where the first has to have happened before the second
        #TODO
        # create -> open check
        relations = {}
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
        missing_dependencies = []
        for i in relations:
            for j in relations[i]:
                if self.manifest_graph.edge_res1_res2(i, j) != "B":
                    missing_dependencies.append([i, j])
        self.logger_result.info(str(missing_dependencies))

