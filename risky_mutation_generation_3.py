class RiskyMutationGeneration:
    def __init__(self, logger, queue_basic_block_trace, queue_mutation, main_lock, args):
        self.main_lock = main_lock
        self.logger = logger
        self.args = args
        self.queue_basic_block_trace = queue_basic_block_trace
        self.mutation_already_generated = []
        self.queue_mutation = queue_mutation

    def process_basic_block_trace_queue(self):
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            state = self.queue_basic_block_trace.get()  # every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            self.process_block_trace(state)

    def process_block_trace(self, state):

        new_mutation = None

        self.mutation_already_generated.append(new_mutation)
        # TODO filter out mutation already done
        self.queue_mutation.put(new_mutation)




        #types
        # ????? check for missing Notifiers -> does it change the state
        pass