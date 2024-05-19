class StateChecker:
    def __init__(self, logger, queue_state, main_lock, puppet_manifest, args):
        self.main_lock = main_lock
        self.logger = logger
        self.puppet_manifest = puppet_manifest
        self.args = args
        self.queue_state = queue_state
        self.state_accumulator = []

    def process_state_queue(self):
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            state = self.queue_state.get() #every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            self.process_state(state)

    def process_state(self, state):
        #TODO compare state with past states
        differences = [] # each list in this list corresponds to differences between states for each saved state
        state = self.convert_to_state_graph(state[1])
        for i in self.state_accumulator:
            differences = self.compare_states(state, i)

        self.state_accumulator.append(state)

        pass

    def compare_states(self, state1, state2):
        both_have = [] # both have these edges
        only_first = [] # only first state has these edges 
        for i in state1:
            if i in state2:
                both_have.append(i)
            else:
                only_first.append(i)
        return only_first
    def convert_to_state_graph(self, state_dir):
        state = []
        original_dir = "main_dir"
        with open(state_dir + "/state.txt", "r") as f:
            state = f.readlines()
        directory = []
        for i in state:
            temp = i.split(" ")
            directory.append(temp)
        directory = directory[1:-2]
        edges = []
        queue = []
        curr_count = 1
        queue.append(original_dir)
        for i in directory:
            queue.append(i[-1][:-1])
            if len(i) <= curr_count:
                for j in range(curr_count-len(i)+1):
                    queue.pop(len(queue)-2)
            edges.append([queue[-2],queue[-1]])
            if curr_count < len(i):
                curr_count+= 1
            else:
                curr_count = len(i)
        return state
