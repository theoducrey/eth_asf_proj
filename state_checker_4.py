class StateChecker:
    def __init__(self, logger, queue_state, main_lock, puppet_manifest, args):
        self.main_lock = main_lock
        self.logger = logger
        self.puppet_manifest = puppet_manifest
        self.args = args
        self.queue_state = queue_state
        self.state_accumulator = []

    def process_state_queue(self, args):
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            state = self.queue_state.get() #every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            self.process_state(state)

    def process_state(self, state):
        #TODO compare state with past states


        self.state_accumulator.append(state)

        pass