import numpy as np


class ManifestGraph:
    def __init__(self, manifest_file):
        self.manifest_file = self.manifest_file
        self.nodes_ressources = {} #list of (type, title)
        self.nbr_nodes = len(self.nodes_ressources)
        # None = no edge, "B" = before, "N" = notify, "R" = require
        self.vertices_relation = np.full((0,0), None, dtype=str, like=None)

    def generate_from_manifest(self):
        graph = None
        with open(self.manifest_file) as manifest_file:
            ressources_raw = manifest_file['resources']
            self.nbr_nodes = len(ressources_raw)
            self.vertices_relation = np.full((self.nbr_nodes, self.nbr_nodes), None, dtype=str, like=None)
            for res_id in range(self.nbr_nodes):
                res = ressources_raw[res_id]
                assert res['title'] not in self.nodes_ressources
                self.nodes_ressources[res['title']] = (res_id, res['type'])
            for res_id in range(self.nbr_nodes):
                res = ressources_raw[res_id]
                if "ensure" in res['parameter']: #TODO check if empty or not
                   self.vertices_relation[res_id, res_id] = "R" #???? "ensure" loop edge
                if "before" in res['parameter']: #add from the relation to the other (before)
                     for res_rel in res['parameter']['before']:
                         id_corresp_resource = self.nodes_ressources[res_rel['title']][0]
                         self.vertices_relation[res_id, id_corresp_resource] = "B"
                if "require" in res['parameter']: #add the inverse edge  (before)
                     for res_rel in res['parameter']['require']:
                         id_corresp_resource = self.nodes_ressources[res_rel['title']][0]
                         self.vertices_relation[id_corresp_resource, res_id] = "B"
                if "notify" in res['parameter']: #create notify edge (notify
                     for res_rel in res['parameter']['notify']:
                         id_corresp_resource = self.nodes_ressources[res_rel['title']][0]
                         self.vertices_relation[res_id, id_corresp_resource] = "N"
                if "subscribe" in res['parameter']: #add the inverse edge (notify)
                     for res_rel in res['parameter']['subscribe']:
                         id_corresp_resource = self.nodes_ressources[res_rel['title']][0]
                         self.vertices_relation[id_corresp_resource, res_id] = "N"


            return graph

        self.ressources = []

    def set_manifest_file(self, manifest_file):
        self.manifest_file = manifest_file
        self.generate_from_manifest()

    def add_mutation(self, mutation):



