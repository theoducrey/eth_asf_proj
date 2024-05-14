import os
import ast
import re
from collections import defaultdict



class TraceHandling:
    def __init__(self, logger, queue_trace, queue_basic_block_trace, main_lock, args):
        self.main_lock = main_lock
        self.logger = logger
        self.args = args
        self.queue_trace = queue_trace
        self.queue_basic_block_trace = queue_basic_block_trace

    def process_tracks(self):
        self.logger.info("trace handling : processing started")
        print("Processing new track")
        while True:
            print("Processing new track")
            trace = self.queue_trace.get()
            self.process_track(trace)



    def process_track(self, trace):
        trace_id = trace[0]
        trace_dir = trace[1]
        trace_target_manifest = trace[2]
        file_accessed = {}  # file_path : [consumed/produced/expunged,...]
        buffer = defaultdict(list)


        #symbolic_link = {}
        FD_table = {0:('stdin',[]), 1:('stdout',[]), 2:('stderr',[])}
        resource_syscall_file = {}
        file_correspondence = defaultdict(list) # list of pair then at the end fusion by looping on every path to replace them with the renamed one, we don't care about timeline because we are checking for resilience against timeline change
        with open(trace_dir + "/strace_output.txt", "r") as f:
            current_resId = None
            for line in f.readlines():
                line = line.strip()

                if current_resId is None:
                    index = line.find("Starting to evaluate the resource")
                    if index != -1:
                        current_resId_left, current_resId_right = line.find('Info: ') + len("Info: "), index - 2
                        current_resId = line[current_resId_left:current_resId_right]
                        if current_resId not in resource_syscall_file: resource_syscall_file[current_resId] = {}
                        continue
                    continue
                else:
                    index = line.find("Evaluated in ")
                    if index != -1:
                        current_resId_left, current_resId_right = line.find('Info: ') + len("Info: "), index - 2
                        current_resId_end = line[current_resId_left:current_resId_right]
                        assert current_resId_end == current_resId
                        current_resId = None
                        continue

                syscall_str = line[6:]

                # handle syscall pausing (unfinished) restart
                if syscall_str[:len('<... ')] == '<... ':
                    resum_index = syscall_str.find(' resumed> ')
                    syscall_name = syscall_str[len('<... '):resum_index]
                    syscall_str = buffer[syscall_name][0] + syscall_str[resum_index + len(' resumed> '):]


                params_left, params_right = syscall_str.find('('), syscall_str.rfind('=') - 2

                syscall_parent_prcess_id = line.strip()[:6]
                syscall_name = syscall_str[:params_left]
                str_params = syscall_str[params_left:params_right + 1]
                syscall_ret = syscall_str[params_right + 2:]

                # handle syscall pausing (unfinished)  start
                unfinished_suffix = ' <unfinished ...>'
                if line[-len(unfinished_suffix):] == unfinished_suffix:
                    buffer[syscall_name].append(syscall_str[:-len(unfinished_suffix)])
                    continue



                str_params = re.sub(r'/\* .*? \*/', '', str_params)

                match syscall_name:
                    case 'execve': #if FD_CLOEXEC set => automatically close the file desciriptor
                        try:
                            params = ast.literal_eval(str_params)
                        except SyntaxError as e:
                            print(e)
                        executable_path = params[0]
                        executable_args = params[1]
                        executable_vars = params[2]
                        if executable_path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][executable_path] = set()
                        resource_syscall_file[current_resId][executable_path].add('execute')
                    case 'access':
                        access_path = str_params[1:str_params.find("\",")]
                        if access_path not in resource_syscall_file[current_resId] : resource_syscall_file[current_resId][access_path] = set()
                        resource_syscall_file[current_resId][access_path].add('accessed')
                    case 'close':
                        right_fd = str_params.rfind(')')
                        fd_to_close = int(str_params[1:right_fd])
                        if fd_to_close in FD_table: #TODO should we consider pointer we close without opening
                            del FD_table[fd_to_close]
                    case 'lstat':
                        left_path = str_params.find(', ')
                        path = str_params[1:left_path-1]
                        if path not in resource_syscall_file[current_resId] : resource_syscall_file[current_resId][path] = set()
                        resource_syscall_file[current_resId][path].add('stats')
                    case 'fcntl':
                        mode = str_params[str_params.rfind(',')+2:str_params.rfind(')')]
                        if mode == 'F_GETFL' or mode == 'F_GETFD':
                            pass
                        elif mode == "FD_CLOEXEC":
                            print(syscall_str)
                        else:
                            print("Not implemented fcntl", syscall_str)
                    case 'getcwd':
                        pass # we don't care TODO don't understand the argument
                    case 'chdir':
                        pass #has this an influence on the path later TODO
                    case "openat":
                        openat_param = str_params.split(',')

                        if 'No such file or directory' in syscall_ret or 'No such device or address' in syscall_ret:
                            if openat_param[1] not in resource_syscall_file[current_resId]:
                                resource_syscall_file[current_resId][openat_param[1]] = set()
                            resource_syscall_file[current_resId][openat_param[1]].add("Not found")
                        else:
                            perms = []
                            if 'O_RDONLY' in openat_param[2]: perms.append('R') #TODO implement the rest add a breakpoint for help
                            #if 'O_' in openat_param[2]: perms.append('W')
                            #if 'O_RDONLY' in openat_param[2]: perms.append('X')
                            new_open_fd = int(syscall_ret[2:])
                            FD_table[new_open_fd] = (openat_param[1][2:-1], perms)
                    case 'statfs':
                        path = str_params.split(',')[0][2:-1]
                        if path not in resource_syscall_file[current_resId] : resource_syscall_file[current_resId][path] = set()
                        resource_syscall_file[current_resId][path].add('stats')
                    case 'readlink':
                        link_path = str_params.split(',')[0][2:-1]
                        target_path = str_params.split(',')[0][2:-1]
                        if link_path in file_correspondence:
                            print("overriding symbolic link probably shoudn't be done")
                        file_correspondence[link_path].append(target_path)
                    case 'chown':
                        pass #TOOD don't perhaps later for mutations
                    case 'write':
                        left_fd2 = str_params.find(',')
                        fd = int(str_params[1:left_fd2])
                        if fd not in FD_table:
                            print("BIG BuG TO FIx close before write why ????? ", syscall_str)
                            continue
                        path = FD_table[fd][0]
                        if path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][path] = set()
                        resource_syscall_file[current_resId][path].add('Write')
                    case 'rmdir':
                        right_path = str_params.find(')')
                        path = str_params[2:right_path - 1]
                        if path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][
                            path] = set()
                        resource_syscall_file[current_resId][path].add('remove')
                    case 'chmod':
                        pass  #TOOD don't perhaps later for mutations
                    case 'rename':
                        pass #TODO don't understand the argument
                        left_path2 = str_params.find(',')
                        right_path2 = str_params.find(')')
                        new_path =  str_params[1:left_path2]
                        old_path =  str_params[left_path2+1:right_path2]
                        file_correspondence[new_path].append((['rename',old_path]))  # file removed
                    case 'unlink':
                        path = str_params[1:-2]
                        if path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][path] = set()
                        resource_syscall_file[current_resId][path].add('remove') #file removed
                    case 'mkdir':
                        path = str_params.split(',')[0][1:]
                        if path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][
                            path] = set()
                        resource_syscall_file[current_resId][path].add('create_dir')  # file removed
                    case 'writev':
                        left_fd_output = str_params.find(',')
                        fd = int(str_params[1:left_fd_output])
                        if fd != 1: # print to stdout are ignore because thread safe
                            raise NotImplemented
                    case 'dup2': #TODO not sure if correct but I inversed the order of the arg from the man page
                        left_fd2, right_fd2 = str_params.find(','), str_params.find(')')
                        fd1 = int(str_params[1:left_fd2])
                        fd2 = int(str_params[left_fd2+1:right_fd2])
                        if fd2 not in FD_table:
                            print("Potential big error in dup2 :", syscall_str)
                            continue
                        FD_table[fd1] = FD_table[fd2]
                    case 'clone':
                        pass # don't care
                    case 'unlinkat':
                        path_left = str_params.find(',')
                        path_right = str_params.rfind(',')
                        path = str_params[path_left+3:path_right-1]
                        if path not in resource_syscall_file[current_resId]: resource_syscall_file[current_resId][
                            path] = set()
                        resource_syscall_file[current_resId][path].add('remove')  # file removed
                    case 'symlink':
                        left_path2 = str_params.find(',')
                        right_path2 = str_params.find(')')
                        new_path = str_params[1:left_path2]
                        old_path = str_params[left_path2 + 1:right_path2]
                        file_correspondence[new_path].append((['rename', old_path]))  # file removed
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
                    case _:
                        if (syscall_str[:len('+++ exited with ')] == '+++ exited with '
                            or syscall_str[:11] == '--- SIGCHLD' or
                                syscall_str[:11] == '--- SIGINT '):
                            pass
                        else:
                            print(syscall_name, end=')\n')


        self.queue_basic_block_trace.put((trace_id, (resource_syscall_file, file_correspondence)))


traceHandling = TraceHandling(None, None, None, None, None)
traceHandling.process_track((0, "output/java_2024-04-27_20-42-20/0", None))

