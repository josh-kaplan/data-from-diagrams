import json 
import collections
import networkx as nx
import matplotlib.pyplot as plt
import drawio
import inferences

class MxGraph():

    def __init__(self, fpath):
        self._objects = []
        self.graph = {
            'elements': [],
            'elementsById': {},
        }
        mxgraph = drawio.mxfile_to_json(fpath)
        self.parse_objects(mxgraph)
        self.build_graph()
    
    def print_graph(self):
        print(json.dumps(self.graph, indent=4))

    def save(self, fname='graph.json'):
        with open(fname, 'w') as f:
            f.write(json.dumps(self.graph, indent=4))


    def parse_objects(self, mxgraph):
        """Loops through all root objects and parses them recursively."""
        for key,val in mxgraph['root'].items():
            self.parse_object(key, val)


    def parse_object(self, key, obj):
        """Recursively parses an mxgraph object, extracting all mxCells and data
        objects. This function has side effects, appending to self._objects."""
        # For lists, loop over items and recurse
        if isinstance(obj, list):
            for i in obj:
                self.parse_object('mxCell', i)
        # XML to dict gives us OrderedDict objects, this is what we expect
        # For objects, merge the MxCell and the object attributes into one result
        elif self.is_dict_like(obj) and key == 'object':
            result = obj['mxCell']
            for k,v in obj.items():
                if k.startswith('@'):
                    result[k] = v
            self._objects.append(result)
        # For plain MxCells, just append the to the graph
        elif self.is_dict_like(obj) and key == 'mxCell':
            self._objects.append(obj)
        else:
            print('Warning: Unknown key. Skipping ...')


    def is_dict_like(self, obj):
        """Returns true if an object is a dictionary like structure."""
        return isinstance(obj, collections.OrderedDict) or isinstance(obj, dict)


    def build_graph(self):
        """Converts the list of raw objects into a graph structure based on
        JSON Graph (https://netflix.github.io/falcor/documentation/jsongraph.html).
        """
        for item in self._objects:
            self.graph['elements'].append({
                '$type': "ref",
                'value': ["elementsById", item['@id']]
            })
            # Flatten mxCells
            if item.get('mxCell', None) is not None:
                item.update(item['mxCell'])
                del item['mxCell']
            self.graph['elementsById'][item['@id']] = item


    def get_all_elements(self):
        return [i for i in self.graph['elementsById'].values() ]

    def to_networkx(self, make_inferences=False):
        G = nx.Graph()
        nodes = []
        edges = []
        labels = {}
        color_map = []
        for element in self.get_all_elements():
            _id = element.get('@id', None)
            if element.get('@vertex', None) == '1':
                if element.get('@style', '').startswith('edgeLabel'):
                    continue
                labels[_id] = element.get('@label', None)
                if labels.get(_id, None) is None:
                    labels[_id] = element.get('@value', None)
                fillColor = '#333';
                for style in element.get('@style', {}).split(';'):
                    if style.startswith('fillColor='):
                        fillColor = style.split('=')[1]
                if fillColor == 'strokeColor':
                    for style in element.get('@style', {}).split(';'):
                        if style.startswith('strokeColor='):
                            fillColor = style.split('=')[1]
                            break
                    else:
                        fillColor = '#333' # default color
                color_map.append(fillColor)
                nodes.append((element.get('@id'), element))
            elif element.get('@edge', None) == '1':
                src = element.get('@source', None)
                tgt = element.get('@target', None)
                edges.append((src, tgt, element))

        G.add_nodes_from(nodes)
        for e in edges:
            print(f'Adding edge {e[0]} --> {e[1]}')
            G.add_edge(e[0], e[1], **e[2])
        if make_inferences == True:
            G = inferences.make_inferences(G)

        self.G = G
        edge_color_map = self.get_edge_color_map()
        self._nx_labels = labels
        self._nx_color_map = color_map
        self._nx_edge_color_map = edge_color_map
        return G, labels, color_map, edge_color_map


    def get_edge_color_map(self):
        result = []
        for u, v, edge in self.G.edges(data=True):
            color = edge.get('color', '#333')
            if color == 'red':
                print(edge)
            result.append(color)
        return result

    def nx_plot(self):
        EDGES = self.G.edges()
        NODES = self.G.nodes()
        pos = nx.spring_layout(self.G, k=0.5)
        nx.draw_networkx_edges(self.G, pos, alpha=0.5, width=2, edge_color=self._nx_edge_color_map)
        nx.draw_networkx_nodes(self.G, pos, node_size=[ 600 for v in NODES ], node_color=self._nx_color_map)
        label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
        nx.draw_networkx_labels(self.G, pos, labels=self._nx_labels, font_size=8, bbox=label_options)
        plt.show()

   
if __name__ == '__main__':
    # Simple tests
    g = MxGraph('examples/simple.drawio.png')
    assert len(g.graph['elements']) == 5
    assert len(g.graph['elementsById'].keys()) == 5

   
    G, color_map, labels = g.to_networkx()
    G = g.make_inferences()
    edge_color_map = g.get_edge_color_map()


    EDGES = G.edges()
    NODES = G.nodes()

    pos = nx.spring_layout(G, k=0.5)
    nx.draw_networkx_edges(G, pos, alpha=0.5, width=2, edge_color=edge_color_map)
    nx.draw_networkx_nodes(G, pos, node_size=[ 600 for v in NODES ], node_color=color_map)
    label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, bbox=label_options)
    #nx.draw(G, pos, with_labels=True, node_color=color_map, labels=labels, font_weight='bold')
    plt.show()

    
