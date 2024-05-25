import random
import string
from collections import defaultdict


class RiskyMutationGeneration:
    def __init__(self, logger, queue_basic_block_trace, queue_mutation, main_lock, args, oneRun=False):
        self.main_lock = main_lock
        self.logger = logger
        self.args = args
        self.queue_basic_block_trace = queue_basic_block_trace
        self.mutation_already_generated = defaultdict(list)
        self.queue_mutation = queue_mutation
        self.oneRun = oneRun

    def process_basic_block_trace_queue(self):
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            block_trace = self.queue_basic_block_trace.get()  # every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            print("process_basic_block_trace_queue")
            self.process_block_trace(block_trace)
            if self.oneRun:
                break

    def process_block_trace(self, block_trace, simultaneous_max_mutations_nbr = 2./10):

        block_trace_id = block_trace[0]
        block_trace_data = block_trace[1]

        if block_trace_data == RuntimeError:  # The manifest failed to run so not possible to generate mutation
            self.logger.info("Run of puppet manifest crash with mutation  so no mutation could be generated")
            return

        # the mutation generation process is independent between resource and apply to each of them
        for ressourceId, files_access in block_trace_data.items():
            if len(files_access) <= 0: continue # no file touch by the manifest so no mutation needed
            new_mutations = [] #elem = (#operation, file,)

            set_threshold_pourcentage = int(len(files_access) * simultaneous_max_mutations_nbr) # correspond to the number of mutation included in a subset of proportion simultaneous_max_mutations_nbr by default correspond to 20% of the original set
            max_subset_size = min(max(set_threshold_pourcentage, 3),
                                  len(files_access))  # max between 3 and 20% but restricted to the size of the upper set, we don't want to have a set of mutation smaller than 3 but still constrains it to the total size of the main set of files
            subset_size = random.randint(1, max_subset_size) # randomly define how big the set f mutation will be still futher restricted by a proba of 70% below

            subset_targeted_file = random.sample(list(files_access.items()), subset_size) # sample the actual set of file which will be targeted by the mutation
            for file, access_type in subset_targeted_file: # for each file targeted define all possible mutation possible depending on there use by puppet, make it also easy to change priority of each mutation
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
                if 'delete' in self.mutation_already_generated[file]: w_delete=0 # only delete the file one time though all the run
                if 'rename' in self.mutation_already_generated[file]: w_rename=0 # only rename the file one time though all the run
                if 'create' in self.mutation_already_generated[file]: w_create=0 # only create the file one time though all the run
                if w_delete + w_rename + w_create == 0: continue

                # choose at random the mutation according to the weights
                randomOperation = random.choices(['delete', 'rename', 'create'], weights=(w_delete, w_rename, w_create))[0]

                self.mutation_already_generated[file].append(randomOperation)

                # some mutation require futher param
                arg2 = None
                match randomOperation:
                    case "rename":
                        arg2 = ''.join(random.choice(string.ascii_lowercase) for _ in range(10)) # give the new name of the file
                    case "delete":
                        pass
                    case "create":
                        pass
                    case _:
                        raise NotImplemented

                new_mutations.append((randomOperation, file, arg2))
            if len(new_mutations) <= 0:
                print("Ressource %s completely explored for run : %s" % (ressourceId, block_trace_id))
                continue
            self.queue_mutation.put((block_trace_id, new_mutations))
