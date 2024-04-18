class TraceAnalyzer:
    def __init__(self, logger, queue_basic_block_trace, main_lock, manifest_graph, args):
        self.main_lock = main_lock
        self.logger = logger
        self.result_logger = logger
        self.manifest_graph = manifest_graph
        self.args = args
        self.queue_basic_block_trace = queue_basic_block_trace

    def process_state_queue(self, args):
        self.logger.info("TraceAnalyzer : processing started")
        while True:
            block_trace = self.queue_basic_block_trace.get()  # every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            self.process_block_trace(block_trace)

    def process_block_trace(self, state):

        #Directy log the result using the result logger
        pass