import os



class TraceHandling:
    def __init__(self, logger, queue_trace, queue_basic_block_trace, main_lock, args):
        self.main_lock = main_lock
        self.logger = logger
        self.args = args
        self.queue_trace = queue_trace
        self.queue_basic_block_trace = queue_basic_block_trace

    def process_mutation_queue(self):
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            trace = self.queue_trace.get() #every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            self.process_mutation(trace)

    def process_mutation(self, trace):
        basic_block_trace = None
        self.queue_basic_block_trace.put(basic_block_trace)
        ("")




