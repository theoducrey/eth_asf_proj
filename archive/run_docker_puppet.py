import os
import subprocess
from sys import stdout


















class SpawnRunPuppet:
    def __init__(self, logger, queue_mutation, queue_trace, queue_state, main_lock, puppet_manifest, args):
        self.main_lock = main_lock
        self.logger = logger
        self.puppet_manifest = puppet_manifest
        self.args = args
        self.queue_mutation = queue_mutation
        self.queue_trace = queue_trace
        self.queue_state = queue_state



    def init_image(self):
        with open("/tmp/output.log", "a") as output:
            subprocess.call("docker pull puppet/puppet-agent", shell=True, stdout=output, stderr=output)

    def process_mutation_queue(self):
        self.logger.info("spawn_run_puppet : processing started")
        while True:
            mutation = self.queue_mutation.get()  # every mutation is a sequence of operation to be applied together before running the puppet manifest on the fresh image
            self.process_mutation(mutation)

    def process_mutation(self, mutation: list):
        pass

    def extract_trace_and_catalog(self):
        pass

def run_puppet_manifest(manifest_path, tmp_output_path, id):
    manifest_path = os.path.abspath(manifest_path)
    tmp_output_path = os.path.abspath(tmp_output_path)
    tmp_output_path = tmp_output_path + "/" + str(id)
    with open("output/output.log", "a") as output:
        subprocess.call("docker pull puppet/puppet-agent", shell=True, stdout=stdout, stderr=stdout)
        subprocess.call(command, shell=True, stdout=stdout, stderr=stdout)
        command_agent = "docker run -i --name puppet-agent-container \
                    -v "+manifest_path+":/etc/puppetlabs/code/environments/production/manifests \
                    -v "+tmp_output_path+(":/output \
                    puppet/puppet-agent")

        command_server = "docker run --net puppet --name puppet-container \
                    -v "+manifest_path+":/etc/puppetlabs/code/environments/production/manifests \
                    -v "+tmp_output_path+":/output \

                    puppet/puppetserver"
        #command = "docker run -it --name puppet-container \
        #            -v "+manifest_path+":/etc/puppetlabs/code/environments/production/manifests \
        #            puppet/puppet-agent"
        command3_in = "strace -o /output/strace_output.txt puppet apply /etc/puppetlabs/code/environments/production/manifests"
        command3 = "docker exec - it puppet-agent-container sh - c \""+command3_in+"\""
        command3_in = "docker cp puppet-agent-container:/opt/puppetlabs/puppet/cache/state/last_run_report.yaml /output"
        command3 = "docker rm puppet-agent-container"
        subprocess.call(command, shell=True, stdout=stdout, stderr=stdout)


def run_puppet_manifest_2(self, manifest_path, module_path, tmp_output_path, id):
    # manifest_path = os.path.abspath(manifest_path)
    tmp_output_path = os.path.abspath(tmp_output_path)
    tmp_output_path = tmp_output_path + "/" + str(id)
    with (open("output/output.log", "a") as output):
        if True:
            output = stdout
        command_1 = "docker-compose up -d"
        command_docker_shell = "docker exec -i puppetserver "
        command_2 = command_docker_shell + "mkdir output/" + str(id)
        command_3 = command_docker_shell + "cp -r /available_manifests/" + manifest_path + " /etc/puppetlabs/code/environments/production/manifests/"
        command_4 = command_docker_shell + "puppet module install alexggolovin-lamp"
        # command_5 = command_docker_shell + "cp -r /modules/" + module_path + " /etc/puppet/code/modules/"
        command_4_alternative = command_docker_shell + "rm /etc/puppetlabs/puppetserver/logback.xml"
        command_5_alternative = command_docker_shell + "cp puppetserver_conf/logback.xml /etc/puppetlabs/puppetserver"
        command_6_alternative = command_docker_shell + "strace -o /output/" + str(id) + (
            "/strace_output.txt puppet apply "  # -f = follow forked childs -y display file name  #-e trace=open,openat,close,read,write,connect,accept
            "/etc/puppetlabs/code/environments"
            "/production/manifests/") + manifest_path

        command_6 = (command_docker_shell +
                     "strace"
                     " -s 300"
                     " -o /output/" + str(id) + "/strace_output.txt" +
                     " -e " + ','.join(syscall_filter) +  # -e trace=open,openat,close,read,write,connect,accept
                     " -f " +  # -f = follow forked childs -y display file name
                     (
                             " puppet apply " +
                             "/etc/puppetlabs/code/environments/production/manifests/" + manifest_path.split('/')[
                                 -1] +
                             " --modulepath /modules/" + module_path +
                             " --debug --evaltrace"
                     ))  # puppet apply /etc/puppetlabs/code/environments/production/manifests/init.pp --debug --evaltrace
        command_7 = command_docker_shell + "bash -c \"puppet catalog find > /output/" + str(
            id) + "/puppet_catalog.json\""
        command_8 = "docker-compose down"
        echo
        "include 'docker'" / etc / puppetlabs / code / environments / production / manifests / init.pp

        subprocess.call(command_1, shell=True, stdout=output, stderr=output)
        subprocess.call(command_2, shell=True, stdout=output, stderr=output)
        subprocess.call(command_3, shell=True, stdout=output, stderr=output)
        # subprocess.call(command_4, shell=True, stdout=output, stderr=output)
        # subprocess.call(command_5, shell=True, stdout=output, stderr=output)
        subprocess.call(command_6, shell=True, stdout=output, stderr=output)
        subprocess.call(command_7, shell=True, stdout=output, stderr=output)
        subprocess.call(command_8, shell=True, stdout=output, stderr=output)


if __name__ == '__main__':
    run_puppet_manifest("manifests", "output",1)
