class Risky_mutation_generation:
    def __init__(self, logger, queue_trace, queue_mutation, main_lock, puppet_manifest, args):
        self.main_lock = main_lock
        self.logger = logger
        self.puppet_manifest = puppet_manifest
        self.args = args
        self.queue_trace = queue_trace
        self.mutation_already_generated = []
        self.queue_mutation = queue_mutation

    def process_state_queue(self, args):
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            state = self.queue_trace.get()  # every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            self.process_trace(state)

    def process_trace(self, state):

        new_mutation = None

        self.mutation_already_generated.append(new_mutation)
        # TODO filter out mutation already done
        self.queue_mutation.put(new_mutation)
        pass