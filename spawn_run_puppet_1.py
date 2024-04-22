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

    def process_mutation(self, mutation: list):
        # generate docker compose file
        image_name = "nothing"
        self.workdir = "/testing"
        text = []
        text.append("FROM ubuntu:22.04")

        # here go all the mutations
        for i in mutation:
            text.append(i)
        
        text.append("WORKDIR " + self.workdir)

        with open("Dockerfile", "w") as file:
            # Writing data to a file
            file.writelines(text)
        # run docker compose file
        os.system("docker build --tag '" + image_name + "'")
        os.system("docker run --detach '" + image_name + "'")
        pass

    def run_puppet_manifest(self):   #TODO in some way add complete trace for each execution with "self.queue_trace.put(trace)" -> this will be automatically futher processed futher by trace_handling
        dir_to_manifest = "something/idk/"
        name_of_manifest = "puppet_manifest.pp"
        dir_and_manifest = os.path.join(dir_to_manifest, name_of_manifest)
        os.system(dir_and_manifest + " > manifest_output.txt")
        trace = self.get_trace()
        state = self.get_state()
        self.queue_trace.put(trace)
        self.queue_state.put(state)

    def get_state(self):
        os.chdir(self.workdir)
        state = []
        queue = []
        all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
        queue = queue + all_subdirs
        while(len(queue) > 0):
            dirs = queue.pop(0)
            dir = os.path.join(self.workdir, dirs)
            os.chdir(dir)
            current = os.getcwd()
            parts = str(current).split("/")
            new = parts[-1]
            prev = parts[-2]
            # state.append([prev, new]) # one possibility
            state.append(prev + " " + new) # allows for easier comparison
            files = os.listdir()
            for i in files:
                parts_files = str(i).split("/")
                new_file = parts_files[-1]
                # state.append([prev, new_file]) # one possibility
                state.append(prev + " " + new_file) # allows for easier comparison
            all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
            queue = queue + all_subdirs
        return state

    def get_trace(self):
        # TODO needs to be done with strace
        with open("manifest_output.txt", "r") as file:
            trace = file.read()
        return trace



