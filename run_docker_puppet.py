import json
import os
import subprocess
from datetime import datetime
from sys import stdout

syscall_filter = [
    "access",
    "chdir",
    "chmod",
    "chown",
    "clone",
    "close",
    "dup",
    "dup2",
    "dup3",
    "execve",
    "fchdir",
    "fchmodat",
    "fchownat",
    "fcntl",
    "fork",
    "getxattr",
    "getcwd",
    "lchown",
    "lgetxattr",
    "lremovexattr",
    "lsetxattr",
    "lstat",
    "link",
    "linkat",
    "mkdir",
    "mkdirat",
    "mknod",
    "open",
    "openat",
    "readlink",
    "readlinkat",
    "removexattr",
    "rename",
    "renameat",
    "rmdir",
    "statfs",
    "symlink",
    "symlinkat",
    "unlink",
    "unlinkat",
    "utime",
    "utimensat",
    "utimes",
    "vfork",
    "write",
    "writev",
]


class SpawnRunPuppet:
    def __init__(self, logger, logger_result_state, logger_result_dependencies, queue_mutation, queue_trace, queue_state, main_lock, target_manifest, oneRun=False):
        self.main_lock = main_lock
        self.logger = logger
        self.target_manifest = target_manifest
        self.queue_mutation = queue_mutation
        self.queue_trace = queue_trace  #contain id of trace
        self.queue_state = queue_state
        self.next_id = len(os.listdir("output")) + 1
        self.existing_ids = set()
        self.output_dir = "output/"+target_manifest+"_" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "/"
        os.makedirs(os.path.join(os.getcwd(), self.output_dir))
        self.current_id = 0
        self.init_image()
        self.oneRun = oneRun

        manifs_f = open('availible_manifest_param.json')
        data = json.load(manifs_f)
        self.manifest_content = data[target_manifest]["manifest_content"]
        self.module_name = data[target_manifest]["module_name"]
        self.module_version = data[target_manifest]["version"]
        self.logger_result_state = logger_result_state
        self.logger_result_dependencies = logger_result_dependencies

    def init_image(self):
        #self.logger.info("Pulling puppetserver image")
        with open("output/SpawnRunPuppet.log", "a") as output:
            subprocess.call("docker pull puppet/puppetserver", shell=True, stdout=output, stderr=output)


    def get_target_catalog(self):
        print("getting target catalog")
        self.run_puppet_manifest_from_name([], self.current_id, [])
        print("target catalog getted ")
        search_dir = self.output_dir + str(self.current_id)+"/"
        with open(search_dir+"puppet_catalog.json") as json_file:
            json_file.readline()
            catalog_json = json.load(json_file)
        self.current_id += 1
        return (self.target_manifest, catalog_json)

    def process_mutation_queue(self):
        print("SpawnRunPuppet:  processing started")
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            mutations = self.queue_mutation.get()  # every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            self.process_mutation(mutations)
            if self.oneRun:
                break

    def process_mutation(self, mutations: list):
        #eg: ("rename", "path_file", "new_name")
        #eg: ("edit_append", "path_file", "new_content")
        #eg: ("edit_prepend", "path_file", "new_content")
        #eg: ("replace", "path_file", "new_content")
        #eg: ("delete", "path_file or dir", "new_name")
        #eg: ("create_file", "path_dir", "new_name")
        #eg: ("create_dir", "path_dir", "new_name")
        #eg: ("rename", "path_file", "new_name")

        mutations_commands = []
        mutations = mutations[1]
        for mut in mutations:
            match mut[0]:
                case "rename":
                    mutations_commands.append("mv "+mut[1]+" "+'/'.join(mut[1].split("/")[:-1])+mut[2])
                case "delete":
                    mutations_commands.append("rm -rf "+mut[1])
                case "create":
                    mutations_commands.append("touch "+mut[1])
                case "edit_append":
                    raise NotImplemented
                case _:
                    raise NotImplemented


        self.run_puppet_manifest_from_name(mutations_commands, self.current_id, mutations)
        local_output_dir = self.output_dir + str(self.current_id)
        self.queue_trace.put((self.current_id, local_output_dir, self.target_manifest))
        self.queue_state.put((self.current_id, local_output_dir))
        self.current_id += 1


    def run_puppet_manifest_from_name(self, mutations_commands, processing_id, mutations):
        local_output_dir = self.output_dir + str(processing_id) + "/"
        os.makedirs(os.path.join(os.getcwd(), local_output_dir))
        with open(local_output_dir + "terminal.log", "a") as output:
            commands = []
            commands.append("docker-compose up -d")
            command_docker_shell = "docker exec -i puppetserver "
            commands.append(command_docker_shell + "mkdir "+local_output_dir)
            commands.append(command_docker_shell + "bash -c  \"echo " + self.manifest_content + " > /etc/puppetlabs/code/environments/production/manifests/init.pp\"")  #echo "include 'docker'" / etc / puppetlabs / code / environments / production / manifests / init.pp
            commands.append(command_docker_shell + "puppet module install " + self.module_name +" --version="+self.module_version)
            commands += [command_docker_shell + "bash -c \"" + mut + "\"" for mut in mutations_commands]
            commands.append((command_docker_shell +
                         "strace"
                         " -s 300"
                         " -o /"+local_output_dir + "/strace_output.txt" +
                         " -e " + ','.join(syscall_filter) +  #-e trace=open,openat,close,read,write,connect,accept
                         " -f " +  # -f = follow forked childs -y display file name
                         (
                                 " puppet apply " +
                                 "/etc/puppetlabs/code/environments/production/manifests/init.pp" +
                                 " --debug --evaltrace"
                         )))  #puppet apply /etc/puppetlabs/code/environments/production/manifests/init.pp --debug --evaltrace
            commands.append(command_docker_shell + "bash -c \"puppet catalog find > /"+local_output_dir + "/puppet_catalog.json\"")

            commands.append(command_docker_shell + "bash -c \"tree > /"+local_output_dir + "/state.txt\"")

            commands.append("docker-compose down")

            for command in commands:
                print("SpawnRunPuppet: " + command)
                subprocess.call(command, shell=True, stdout=output, stderr=output)

        if not os.path.exists(local_output_dir + "puppet_catalog.log") or not os.path.exists(local_output_dir + "strace_output.txt"):
            self.logger_result_state.info("Run of puppet manifest crash with mutation : %s" % (str(mutations)))
            self.logger_result_dependencies.info("Run of puppet manifest crash with mutation : %s" % (str(mutations)))




#if __name__ == '__main__':
    #spawn = SpawnRunPuppet(None, None, None, None, None)
    #spawn.run_puppet_manifest_from_name("include java", "puppetlabs-java --version 11.0.0", 9)
    #spawn.run_puppet_manifest("albatrossflavour-os_patching/init.pp", "albatrossflavour-os_patching-0.21.0", "output",8)
