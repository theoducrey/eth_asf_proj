import os
    import subprocess


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


    def run_puppet_manifest(self, manifest_path, tmp_output_path, id):
        tmp_output_path = tmp_output_path + "/" + id
        with open("/tmp/output.log", "a") as output:
            command = "docker run -it --name puppet-container \
                        -v "+manifest_path+":/etc/puppetlabs/code/environments/production/manifests \
                        -v "+tmp_output_path+":/output \
                        puppet/puppet-agent"
            #command = "docker run -it --name puppet-container \
            #            -v "+manifest_path+":/etc/puppetlabs/code/environments/production/manifests \
            #            puppet/puppet-agent"
            command3_in = "strace -o /output/strace_output.txt puppet apply /etc/puppetlabs/code/environments/production/manifests"
            command3_in = "docker cp puppet-container:/opt/puppetlabs/puppet/cache/state/last_run_report.yaml /output"
            command3 = "docker rm puppet-container"
            subprocess.call(command, shell=True, stdout=output, stderr=output)


def spawning_thread()
docker pull puppet/puppet-agent
