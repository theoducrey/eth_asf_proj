import os



class Spawn_run_puppet:
    def __init__(self, logger, main_lock, puppet_manifest, args):
        self.main_lock = main_lock
        self.logger = logger
        self.puppet_manifest = puppet_manifest
        self.args = args

    def process_mutation_queue(self, args, queue_mutation, queue_trace):
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            mutation = queue_mutation.get() #every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
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

    def run_puppet_manifest(self):
        self.trace = []
        self.state = []

    def get_state(self):
        return self.state

    def get_trace(self):
        return self.trace



