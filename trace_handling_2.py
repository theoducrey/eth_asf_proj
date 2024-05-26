import os
import ast
import re
import json
from multiprocessing import Queue

from manifestGraph import ManifestGraph
from risky_mutation_generation_3 import RiskyMutationGeneration
from trace_analyzer_5 import TraceAnalyzer
from collections import defaultdict



class TraceHandling:
    def __init__(self, logger, queue_trace, queue_basic_block_trace_for_mutation, queue_basic_block_trace_for_checker, main_lock, args, oneRun=False):
        self.main_lock = main_lock
        self.logger = logger
        self.args = args
        self.queue_trace = queue_trace
        self.queue_basic_block_trace_for_mutation = queue_basic_block_trace_for_mutation
        self.queue_basic_block_trace_for_checker = queue_basic_block_trace_for_checker
        self.oneRun = oneRun

    def process_tracks(self):
        self.logger.info("trace handling : processing started")
        while True:
            trace = self.queue_trace.get()
            print("process_tracks")
            self.process_track(trace)
            if self.oneRun:
                break



    def process_track(self, trace):
        trace_id = trace[0]
        trace_dir = trace[1]
        #trace_target_manifest = trace[2]
        #file_accessed = {}  # file_path : [consumed/produced/expunged,...]

        if not os.path.exists(trace_dir + "/strace_output.txt"): # handle where the manifest run wasn't succesful and crash in this case the trace is basically RuntimeError
            self.queue_basic_block_trace_for_mutation.put((trace_id, RuntimeError))
            self.queue_basic_block_trace_for_checker.put((trace_id, RuntimeError))
            return

        buffer = defaultdict(list) # save the unfinished syscall

        FD_table = {0:('stdin',[]), 1:('stdout',[]), 2:('stderr',[])} # by default a system start with this triple of pipe
        working_dir = '' # handle the change of base directory for the paths retrieved
        resource_syscall_file = {} # end return value, save all files accessed by each resource and the operations performed on them
        file_correspondence = dict() # list of pair renaming and linking then at the end fusion the pair by looping on every path to replace them with the renamed one, we don't care about timeline because we are checking for resilience against resource reordering
        with open(trace_dir + "/strace_output.txt", "r") as f:
            current_resId = None
            for line in f.readlines(): # for each line in the trace
                line = line.strip()
                if current_resId is None: # if not inside the block of one of the ressource, search for the puppet debugging print indicating the start of a resource processing
                    index = line.find("Starting to evaluate the resource")
                    if index != -1:
                        current_resId_left, current_resId_right = line.find('Info: ') + len("Info: "), index - 2
                        current_resId = line[current_resId_left:current_resId_right]
                        if current_resId[0] == "/": current_resId = current_resId[1:] # in the debug output the type of the resource may be precesseded by a / which need to be removed
                        dash_index = current_resId.find('/') # check if futher dash exist
                        if dash_index!= -1 : current_resId = current_resId[:current_resId.find('/')] # only take main ressource id not the rest
                        if current_resId not in resource_syscall_file: resource_syscall_file[current_resId] = {}
                        continue
                    continue
                else:
                    index = line.find("Evaluated in ") # at this point we are interpreting every line as being part of the processing of a resource, we check if the current line endicate the end of the processing of the current resource
                    if index != -1:
                        current_resId_left, current_resId_right = line.find('Info: ') + len("Info: "), index - 2
                        current_resId_end = line[current_resId_left:current_resId_right]
                        if current_resId_end[0] == "/": current_resId_end = current_resId_end[1:line.find("/")]
                        dash_index = current_resId_end.find('/')
                        if dash_index!= -1 : current_resId_end = current_resId_end[:current_resId_end.find('/')] # only take main ressource id
                        assert current_resId_end == current_resId # no resource are executed in parallel so to obtain/close a second resource the first one is first closed
                        current_resId = None
                        continue

                syscall_str = line[6:]

                # handle syscall pausing (unfinished) restart
                if syscall_str[:len('<... ')] == '<... ':
                    resum_index = syscall_str.find(' resumed> ')
                    syscall_name = syscall_str[len('<... '):resum_index]
                    syscall_str = buffer[syscall_name][0] + syscall_str[resum_index + len(' resumed> '):]


                params_left, params_right = syscall_str.find('('), syscall_str.rfind('=') - 2

                syscall_timestamp = line.strip()[:6]
                syscall_name = syscall_str[:params_left] # extract the name of the syscall
                str_params = syscall_str[params_left:params_right + 1] # extract the parameters of the syscall
                syscall_ret = syscall_str[params_right + 2:] # extract the return value of the syscall

                # handle syscall pausing (unfinished)  start
                unfinished_suffix = ' <unfinished ...>'
                if line[-len(unfinished_suffix):] == unfinished_suffix:
                    buffer[syscall_name].append(syscall_str[:-len(unfinished_suffix)])
                    continue

                # remove comments from the trace file
                str_params = re.sub(r'/\* .*? \*/', '', str_params)

                match syscall_name:
                    case 'execve': #if FD_CLOEXEC set => automatically close the file desciriptor
                        try:
                            params = ast.literal_eval(str_params)
                        except SyntaxError as e:
                            self.logger.info(str(e))
                        executable_path = working_dir+str(params[0])
                        executable_args = params[1]
                        executable_vars = params[2]
                        if executable_path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][str(executable_path)] = set()
                        resource_syscall_file[current_resId][str(executable_path)].add('execute')
                    case 'access':
                        access_path = working_dir+str_params[2:str_params.find("\",")]
                        if access_path not in resource_syscall_file[current_resId] : resource_syscall_file[current_resId][access_path] = set()
                        resource_syscall_file[current_resId][access_path].add('accessed')
                    case 'close':
                        right_fd = str_params.rfind(')')
                        fd_to_close = int(str_params[1:right_fd])
                        if fd_to_close in FD_table:
                            del FD_table[fd_to_close]
                    case 'lstat':
                        left_path = str_params.find(', ')
                        path = working_dir+str_params[2:left_path-1]
                        if path not in resource_syscall_file[current_resId] :
                            resource_syscall_file[current_resId][path] = set()
                        resource_syscall_file[current_resId][path].add('stats')
                    case 'fcntl':
                        mode = str_params[str_params.rfind(',')+2:str_params.rfind(')')]
                        if mode == 'F_GETFL' or mode == 'F_GETFD':
                            pass
                        elif mode == "FD_CLOEXEC":
                            pass
                            #self.logger.info(str(syscall_str))
                        else:
                            pass
                            #self.logger.info("Not implemented fcntl : %s" % (str(syscall_str)))
                    case 'getcwd':
                        pass
                    case 'chdir':
                        new_root_right = str_params.find(')')
                        new_root = str_params[1:new_root_right]
                        while True:
                            if new_root[:2] == '../':
                                new_root = new_root[2:]
                                working_dir = working_dir[:-1]
                                working_dir = working_dir[:working_dir[:-1].rfind('/')]
                            elif new_root[:2] == './':
                                new_root = new_root[1:]
                                working_dir = working_dir[:-1]
                                working_dir = working_dir[:working_dir[:-1].rfind('/')]
                            else:
                                break
                        working_dir = working_dir + new_root + '/'
                    case "openat":
                        openat_param = str_params.split(',')

                        if 'No such file or directory' in syscall_ret or 'No such device or address' in syscall_ret:
                            if openat_param[1] not in resource_syscall_file[current_resId]:
                                resource_syscall_file[current_resId][openat_param[1][2:-1]] = set()
                            resource_syscall_file[current_resId][openat_param[1][2:-1]].add("Not found")
                        else:
                            perms = []
                            if 'O_RDONLY' in openat_param[2]: perms.append('R')
                            #if 'O_' in openat_param[2]: perms.append('W')
                            #if 'O_RDONLY' in openat_param[2]: perms.append('X')
                            new_open_fd = int(syscall_ret[2:])
                            FD_table[new_open_fd] = (openat_param[1][2:-1], perms)
                    case 'statfs':
                        path = working_dir+str_params.split(',')[0][2:-1]
                        if path not in resource_syscall_file[current_resId] : resource_syscall_file[current_resId][path] = set()
                        resource_syscall_file[current_resId][path].add('stats')
                    case 'readlink':
                        link_path = working_dir+str_params.split(',')[0][2:-1]
                        target_path = working_dir+str_params.split(',')[0][2:-1]
                        if link_path in file_correspondence:
                            pass
                            #self.logger.info("overriding symbolic link probably shoudn't be done")
                        file_correspondence[link_path] =('link', target_path)
                    case 'chown':
                        pass #TOOD don't perhaps later for mutations
                    case 'write':
                        left_fd2 = str_params.find(',')
                        fd = int(str_params[1:left_fd2])
                        if fd not in FD_table:
                            #self.logger.info("close before write ignored %s" % (str(syscall_str)))
                            continue
                        path = FD_table[fd][0]
                        if path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][path] = set()
                        resource_syscall_file[current_resId][path].add('write')
                    case 'rmdir':
                        right_path = str_params.find(')')
                        path = working_dir+str_params[2:right_path - 1]
                        if path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][
                            path] = set()
                        resource_syscall_file[current_resId][path].add('remove')
                    case 'chmod':
                        pass
                    case 'fchmodat':
                        pass
                    case 'rename':
                        pass #TODO don't understand the argument
                        left_path2 = str_params.find(',')
                        right_path2 = str_params.find(')')
                        if str_params[1]=='0':
                            new_path = working_dir+str_params[1:left_path2]
                        else:
                            new_path = working_dir+str_params[2:left_path2-1]
                        if str_params[left_path2 + 2]=='0':
                            old_path = working_dir+str_params[left_path2 + 2:right_path2]
                        else:
                            old_path = working_dir+str_params[left_path2 + 3:right_path2-1]
                        file_correspondence[new_path] = ('rename', old_path) # file removed
                    case 'unlink':
                        path = working_dir+str_params[2:-2]
                        if path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][path] = set()
                        resource_syscall_file[current_resId][path].add('remove') #file removed
                    case 'mkdir':
                        path = working_dir+str_params.split(',')[0][1:]
                        if path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][
                            path] = set()
                        resource_syscall_file[current_resId][path].add('create')  # file removed
                    case 'writev':
                        left_fd_output = str_params.find(',')
                        fd = int(str_params[1:left_fd_output])
                        if fd != 1: # print to stdout are ignore because thread safe
                            self.logger.info("Write syscall are not tacken into account with the current version of the testing pipeline")
                            continue
                            #raise NotImplemented
                    case 'dup2': #TODO not sure if correct but I inversed the order of the arg from the man page
                        left_fd2, right_fd2 = str_params.find(','), str_params.find(')')
                        fd1 = int(str_params[1:left_fd2])
                        fd2 = int(str_params[left_fd2+1:right_fd2])
                        if fd2 not in FD_table:
                            #self.logger.info(" dup2 ignored missing filedescriptor: %s" % (str(syscall_str)))
                            continue
                        FD_table[fd1] = FD_table[fd2]
                    case 'dup':
                        right_old_fd =  str_params.find(')')
                        old_fd = int(str_params[1:right_old_fd])
                        new_fd = int(syscall_ret[2:])
                        if old_fd not in FD_table:
                            #self.logger.info("dup ignored missing filedescriptor : %s" % (str(syscall_str)))
                            continue
                        FD_table[new_fd] = FD_table[old_fd]
                    case 'clone':
                        pass # don't care
                    case 'unlinkat':
                        path_left = str_params.find(',')
                        path_right = str_params.rfind(',')
                        path = working_dir+str_params[path_left+3:path_right-1]
                        if path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][
                            path] = set()
                        resource_syscall_file[current_resId][path].add('remove')  # file removed
                    case 'symlink':
                        left_path2 = str_params.find(',')
                        right_path2 = str_params.find(')')
                        if str_params[1]=='0':
                            new_path = working_dir+str_params[1:left_path2]
                        else:
                            new_path = working_dir+str_params[2:left_path2-1]
                        if str_params[left_path2 + 2]=='0':
                            old_path = working_dir+str_params[left_path2 + 2:right_path2]
                        else:
                            old_path = working_dir+str_params[left_path2 + 3:right_path2-1]
                        file_correspondence[new_path] = ('rename', old_path) # file removed
                    case 'fchownat':
                        pass # don't care about permission change
                    case 'utimensat':
                        pass # don't care about timestamp change
                    case 'mkdirat':
                        pass # no path in the parameters
                    case 'utimes':
                        pass # we don't care no real modification
                    case 'lchown':
                        pass # change owner of symbolic link we don't care
                    case 'link':
                        left_path2 = str_params.find(',')
                        right_path2 = str_params.find(')')
                        if str_params[1]=='0':
                            old_path = working_dir+str_params[1:left_path2]
                        else:
                            old_path = working_dir+str_params[2:left_path2-1]
                        if str_params[left_path2 + 2]=='0':
                            new_path = working_dir+str_params[left_path2 + 2:right_path2]
                        else:
                            new_path = working_dir+str_params[left_path2 + 3:right_path2-1]
                        file_correspondence[new_path] = ('rename', old_path) # file removed
                    case 'fchdir':
                        try:
                            new_root = FD_table[int(str_params[str_params.find('(')+1:str_params.find(')')])][0]
                        except KeyError as e:
                            #self.logger.info("Trying to change working directory to a file pointer not open or already closed .")
                            continue
                        while True:
                            if new_root[:2]=='../':
                                new_root = new_root[2:]
                                working_dir = working_dir[:-1]
                                working_dir = working_dir[:working_dir[:-1].rfind('/')]
                            elif new_root[:2] == './':
                                new_root = new_root[1:]
                                working_dir = working_dir[:-1]
                                working_dir = working_dir[:working_dir[:-1].rfind('/')]
                            else:
                                break
                        working_dir = working_dir+new_root+'/'

                        continue # this may need to be implemented in the future version
                    case _:
                        if (
                                syscall_str[:len('+++ exited with ')] == '+++ exited with ' or
                                syscall_str[:11] == '--- SIGCHLD' or
                                syscall_str[:11] == '--- SIGINT ' or
                                syscall_str[:11] == '--- SIGSEGV' or
                                syscall_str == '+++ killed by SIGINT +++'
                        ):
                            pass
                        else:
                            print(syscall_name, end='----Line from state that wasn t understood\n')

        for resId in resource_syscall_file:
            # for each file we check if it was rename at one point by checking if it exist in file_correspondence, if it is the case we replce it with the renamed version else we keep it as is
            resource_syscall_file[resId] = {k if k not in file_correspondence.keys() else file_correspondence[k][1]: v for k, v in resource_syscall_file[resId].items()}

        # we happen the result trace representation for both processing in the mutation generator and dependecies checker
        self.queue_basic_block_trace_for_mutation.put((trace_id, resource_syscall_file))
        self.queue_basic_block_trace_for_checker.put((trace_id, resource_syscall_file))


