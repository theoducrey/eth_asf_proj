import numpy as np


class ManifestGraph:
    def __init__(self, catalog_json):
        self.nodes_resources = {} #type[title]: (id, title, type)
        self.nbr_nodes = len(self.nodes_resources)
        # None = no edge, "B" = before, "N" = notify, "R" = require
        self.vertices_relation = np.full((0,0), None, dtype=str, like=None) # the initial graph is empty and count 0 resources
        self.set_catalog_file(catalog_json)

    '''
    A getter which given the name of two resources check if a relation exist in the graph from the first resource to the second one 
    res1_title -> res2_title
    '''
    def edge_res1_res2(self, res1_title, res2_title):
        return self.vertices_relation[self.nodes_resources[res1_title][0], self.nodes_resources[res2_title][0]]

    def generate_from_manifest(self):
        ressources_raw = self.catalog_json['resources']
        self.nbr_nodes = len(ressources_raw) # count the nbr of resource in the catalog
        self.nodes_resources = {}
        self.vertices_relation = np.full((self.nbr_nodes, self.nbr_nodes), None, dtype=str, like=None) # empty matrix as if no relation existed
        # for each resource in the file add an entry into the nodes_resources to make it 
        for res_id in range(self.nbr_nodes):
            res = ressources_raw[res_id]
            assert res['title'] not in self.nodes_resources
            str_id = res['type']+"["+res['title']+"]" # ressource_type[ressource_title] which correspond to the format use in the trace
            self.nodes_resources[str_id] = (res_id, res['title'], res['type'])
        for res_id in range(self.nbr_nodes):
            res = ressources_raw[res_id]
            if "parameters" not in res: continue
            if "ensure" in res['parameters']:
               self.vertices_relation[res_id, res_id] = "R"
            if "before" in res['parameters']: #add from the relation to the other (before)
                before = res['parameters']['before'] if isinstance(res['parameters']['before'], list) else [res['parameters']['before']] # the parameter may be a list in some case, to better handle the different situation we ensure it becomes a list
                for res_rel in before:
                     id_corresp_resource = self.nodes_resources[res_rel][0]
                     self.vertices_relation[res_id, id_corresp_resource] = "B"
            if "require" in res['parameters']: #add the inverse edge  (before)
                require = res['parameters']['require'] if isinstance(res['parameters']['require'], list) else [res['parameters']['require']] # the parameter may be a list in some case, to better handle the different situation we ensure it becomes a list
                for res_rel in require:
                     id_corresp_resource = self.nodes_resources[res_rel][0]
                     self.vertices_relation[id_corresp_resource, res_id] = "B"
            if "notify" in res['parameters']: #create notify edge (notify
                notify = res['parameters']['notify'] if isinstance(res['parameters']['notify'], list) else [res['parameters']['notify']] # the parameter may be a list in some case, to better handle the different situation we ensure it becomes a list
                for res_rel in notify:
                    id_corresp_resource = self.nodes_resources[res_rel][0]
                    self.vertices_relation[res_id, id_corresp_resource] = "N"
            if "subscribe" in res['parameters']: #add the inverse edge (notify)
                subscribe = res['parameters']['subscribe'] if isinstance(res['parameters']['subscribe'], list) else [res['parameters']['subscribe']] # the parameter may be a list in some case, to better handle the different situation we ensure it becomes a list
                for res_rel in subscribe:
                     id_corresp_resource = self.nodes_resources[res_rel][0]
                     self.vertices_relation[id_corresp_resource, res_id] = "N"
        for edge in self.catalog_json['edges']: # the catalog second way of coding relation is using a list of edges, we just save each edge into our relation matrix 'vertices_relation'
            src_id = self.nodes_resources[edge["source"]][0]
            tgt_id = self.nodes_resources[edge["target"]][0]
            self.vertices_relation[src_id, tgt_id] = "B"

    def set_catalog_file(self, catalog_json): # allow to set a new catalog and recompute the graph according to it
        self.target_manifest = catalog_json[0]
        self.catalog_json = catalog_json[1]
        self.generate_from_manifest()




