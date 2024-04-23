import os
import subprocess
from sys import stdout


#new version
#Terminal 1  (in docker_testbench directory)
#docker-compose up
#Terminal 2
#docker exec -it puppetserver /bin/bash
#puppet apply /etc/puppetlabs/code/puppetlabs-apache-12.1.0/manifests/
#or
#puppet apply /etc/puppetlabs/code/examples/
#or
#...















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




if __name__ == '__main__':
    run_puppet_manifest("manifests", "output",1)
