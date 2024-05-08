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

    def process_block_trace(self, mgraph: ManifestGraph, trace):
        #Directy log the result using the result logger
        #TODO
        # create -> open check
        relations = {}
        for i in trace :
            for j in i['new']:
                for k in trace:
                    if k != i and j in k['open']:
                        relations[i][k] = 0
        missing_dependencies = []
        for i in relations:
            for j in relations[i]:
                if mgraph.edge_res1_res2(i, j) != "B":
                    missing_dependencies.append([i, j])
        return missing_dependencies
