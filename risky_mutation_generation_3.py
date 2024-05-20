import random
from collections import defaultdict


class RiskyMutationGeneration:
    def __init__(self, logger, queue_basic_block_trace, queue_mutation, main_lock, args):
        self.main_lock = main_lock
        self.logger = logger
        self.args = args
        self.queue_basic_block_trace = queue_basic_block_trace
        self.mutation_already_generated = defaultdict(list)
        self.queue_mutation = queue_mutation

    def process_basic_block_trace_queue(self):
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            block_trace = self.queue_basic_block_trace.get()  # every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            self.process_block_trace(block_trace)

    def process_block_trace(self, block_trace, simultaneous_max_mutations_nbr = 2./10):

        block_trace_id = block_trace[0]
        block_trace_data = block_trace[1]

        #new_mutations_run = []

        for ressourceId, files_access in block_trace_data.items():
            if len(files_access) <= 0: continue
            new_mutations = [] #elem = (#operation, file,)

            set_threshold_pourcentage = int(len(files_access) * simultaneous_max_mutations_nbr)
            max_subset_size = min(max(set_threshold_pourcentage, 3),
                                  len(files_access))  # max between 3 and 20% but restricted to the size of the upper set
            subset_size = random.randint(1, max_subset_size)

            subset_targeted_file = random.sample(list(files_access.items()), subset_size)
            for file, access_type in subset_targeted_file:
                w_delete, w_rename, w_create = 0, 0, 0
                if 'execute' in access_type: w_delete += 1; w_rename += 1; w_create += 0
                if 'remove' in access_type: w_delete += 1; w_rename += 1; w_create += 1
                if 'rename' in access_type: w_delete += 1; w_rename += 1; w_create += 1

                if 'accessed' in access_type: w_delete += 1; w_rename += 1; w_create += 0
                if 'stats' in access_type: w_delete += 1; w_rename += 1; w_create += 0
                if 'Not found' in access_type: w_delete += 0; w_rename += 0; w_create += 1
                if 'write' in access_type: w_delete += 1; w_rename += 1; w_create += 0
                if 'create_dir' in access_type: w_delete += 0; w_rename += 0; w_create += 1

                # do nothing
                if random.random() < 7./10 : continue

                # may be remove in future version to explore more possible bug interaction
                if 'delete' in self.mutation_already_generated[file]: w_delete=0
                if 'rename' in self.mutation_already_generated[file]: w_rename=0
                if 'create' in self.mutation_already_generated[file]: w_create=0
                if w_delete + w_rename + w_create == 0: continue

                randomOperation = random.choices(['delete', 'rename', 'create'], weights=(w_delete, w_rename, w_create))

                self.mutation_already_generated[file].append(randomOperation)
                new_mutations.append((randomOperation, file))
            if len(new_mutations) <= 0:
                print("Ressource %s completely explored for run : %s" % (ressourceId, block_trace_id))
            self.queue_mutation.put((block_trace_id, new_mutations))

        #  check for missing Notifiers -> does it change the state
