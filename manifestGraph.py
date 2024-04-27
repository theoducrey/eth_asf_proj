import numpy as np


class ManifestGraph:
    def __init__(self, catalog_json):
        self.nodes_ressources = {} #type[title]: (id, title, type)
        self.nbr_nodes = len(self.nodes_ressources)
        # None = no edge, "B" = before, "N" = notify, "R" = require
        self.vertices_relation = np.full((0,0), None, dtype=str, like=None)
        self.set_catalog_file(catalog_json)


    def generate_from_manifest(self):
        ressources_raw = self.catalog_json['resources'] #TODO we may want to consider an empty graph (no ressources) which can be expanded manually
        self.nbr_nodes = len(ressources_raw)
        self.nodes_ressources = {}
        self.vertices_relation = np.full((self.nbr_nodes, self.nbr_nodes), None, dtype=str, like=None)
        for res_id in range(self.nbr_nodes):
            res = ressources_raw[res_id]
            assert res['title'] not in self.nodes_ressources
            str_id = res['type']+"["+res['title']+"]"
            self.nodes_ressources[str_id] = (res_id, res['title'], res['type'])
        for res_id in range(self.nbr_nodes):
            res = ressources_raw[res_id]
            if "parameters" not in res: continue
            if "ensure" in res['parameters']: #TODO check if empty or not
               self.vertices_relation[res_id, res_id] = "R" #???? "ensure" loop edge
            if "before" in res['parameters']: #add from the relation to the other (before)
                before = res['parameters']['before'] if isinstance(res['parameters']['before'], list) else [res['parameters']['before']]
                for res_rel in before:
                     id_corresp_resource = self.nodes_ressources[res_rel][0]
                     self.vertices_relation[res_id, id_corresp_resource] = "B"
            if "require" in res['parameters']: #add the inverse edge  (before)
                require = res['parameters']['require'] if isinstance(res['parameters']['require'], list) else [res['parameters']['require']]
                for res_rel in require:
                     id_corresp_resource = self.nodes_ressources[res_rel][0]
                     self.vertices_relation[id_corresp_resource, res_id] = "B"
            if "notify" in res['parameters']: #create notify edge (notify
                notify = res['parameters']['notify'] if isinstance(res['parameters']['notify'], list) else [res['parameters']['notify']]
                for res_rel in notify:
                     id_corresp_resource = self.nodes_ressources[res_rel][0]
                     self.vertices_relation[res_id, id_corresp_resource] = "N"
            if "subscribe" in res['parameters']: #add the inverse edge (notify)
                subscribe = res['parameters']['subscribe'] if isinstance(res['parameters']['subscribe'], list) else [res['parameters']['subscribe']]
                for res_rel in subscribe:
                     id_corresp_resource = self.nodes_ressources[res_rel][0]
                     self.vertices_relation[id_corresp_resource, res_id] = "N"
            #todo what is the parameter version
        for edge in self.catalog_json['edges']:
            src_id = self.nodes_ressources[edge["source"]][0]
            tgt_id = self.nodes_ressources[edge["target"]][0]
            self.vertices_relation[src_id, tgt_id] = "B"

    def set_catalog_file(self, catalog_json):
        self.target_manifest = catalog_json[0]
        self.catalog_json = catalog_json[1]
        self.generate_from_manifest()




