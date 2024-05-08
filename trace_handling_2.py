import os



class TraceHandling:
    def __init__(self, logger, queue_trace, queue_basic_block_trace, main_lock, args):
        self.main_lock = main_lock
        self.logger = logger
        self.args = args
        self.queue_trace = queue_trace
        self.queue_basic_block_trace = queue_basic_block_trace

    def process_tracks(self):
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            trace = self.queue_trace.get()
            self.process_track(trace)

    def process_track(self, trace):
        trace_id = trace[0]
        trace_dir = trace[1]
        trace_target_manifest = trace[2]
        file_accessed = {} # file_path : [consumed/produced/expunged,...]
        list_of_syscall = set()
        with open(trace_dir+"/strace_output.txt", "r") as f:
            current_id = None
            for line in f.readlines():
                syscall_str = line.strip()[6:]
                syscall_name = syscall_str.split('(')[0]
                match syscall_name:
                    case 'execve':
                        pass
                    case 'access':
                        pass
                    case 'close':
                        pass
                    case 'lstat':
                        pass
                    case 'fcntl':
                        pass
                    case 'getcwd':
                        pass
                    case 'chdir':
                        pass
                    case "openat":
                        pass
                    case 'statfs':
                        pass
                    case 'readlink':
                        pass
                    case 'chown':
                        pass
                    case 'write':
                        pass
                    case 'rmdir':
                        pass
                    case 'chmod':
                        pass
                    case 'rename':
                        pass
                    case 'unlink':
                        pass
                    case 'mkdir':
                        pass
                    case 'writev':
                        pass
                    case 'dup2':
                        pass
                    case 'clone':
                        pass
                    case 'unlinkat':
                        pass
                    case 'symlink':
                        pass
                    case 'fchownat':
                        pass
                    case 'utimensat':
                        pass
                    case 'mkdirat':
                        pass
                    case 'utimes':
                        pass
                    case 'utimes':
                        pass
                    case 'utimes':
                        pass
                    case _:
                        print(syscall_name, end='\n')
    #

        basic_block_trace = None
        self.queue_basic_block_trace.put(basic_block_trace)
        ("")

traceHandling = TraceHandling(None, None,None, None, None)
traceHandling.process_track((0, "output/java_2024-04-27_20-42-20/0", None))


