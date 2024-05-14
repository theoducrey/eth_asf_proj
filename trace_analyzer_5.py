from manifestGraph import ManifestGraph
class TraceAnalyzer:
    def __init__(self, logger, queue_basic_block_trace, main_lock, manifest_graph, args):
        self.main_lock = main_lock
        self.logger = logger
        self.result_logger = logger
        self.manifest_graph = manifest_graph
        self.args = args
        self.queue_basic_block_trace = queue_basic_block_trace





    def process_basic_block_trace_queue(self):
        self.logger.info("TraceAnalyzer : processing started")
        while True:
            block_trace = self.queue_basic_block_trace.get()  # every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            self.process_block_trace(block_trace)

    def process_block_trace(self, mgraph: ManifestGraph, trace_old):
        trace = {}
        for i in trace_old:
            for j in trace_old[i]:
                for k in trace_old[i][j]:
                    if i not in trace or k not in trace[i]:
                        trace[i][k] = {j}
                    else:
                        trace[i][k].add(j)

        #Directy log the result using the result logger
        before_after = [['A', 'remove']] # list of tuples(lists), these tuples contain pair where the first has to have happened before the second
        #TODO
        # create -> open check
        relations = {}
        for relation in before_after:
            for i in trace :
                for j in trace[i][relation[0]]:
                    for k in trace:
                        if k != i and j in trace[k][relation[1]]:
                            relations[i][k] = 0
        missing_dependencies = []
        for i in relations:
            for j in relations[i]:
                if mgraph.edge_res1_res2(i, j) != "B":
                    missing_dependencies.append([i, j])
        return missing_dependencies
