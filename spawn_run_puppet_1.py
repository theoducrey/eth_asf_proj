import os



class SpawnRunPuppet:
    def __init__(self, logger, queue_mutation, queue_trace, queue_state, main_lock, puppet_manifest, args):
        self.main_lock = main_lock
        self.logger = logger
        self.puppet_manifest = puppet_manifest
        self.args = args
        self.queue_mutation = queue_mutation
        self.queue_trace = queue_trace
        self.queue_state = queue_state

    def process_mutation_queue(self):
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            mutation = self.queue_mutation.get() #every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            self.process_mutation(mutation)

    def process_mutation(self, mutation: list[str]):
        # generate docker compose file
        text = []



        image_name = "nothing"

        with open("Dockerfile", "w") as file:
            # Writing data to a file
            file.writelines(text)
        # run docker compose file
        os.system("docker build --tag '" + image_name + "'")
        os.system("docker run --detach '" + image_name + "'")
        pass

    def run_puppet_manifest(self):   #TODO in some way add complete trace for each execution with "self.queue_trace.put(trace)" -> this will be automatically futher processed futher by trace_handling
        self.trace = []
        self.state = []

    def get_state(self):
        return self.state

    def get_trace(self):
        return self.trace



