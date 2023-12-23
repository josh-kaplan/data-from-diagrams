"""
This file is used to index the graph using Neo4j. Note that this will
delete all items in the database each time it is run. It is intended for
development and analytics purposes only.
"""

from py2neo import Graph, Node, Relationship

def connect():
    neo4j = Graph(host='localhost', port=7687, auth=("neo4j", "changeme"))
    neo4j.delete_all()
    return neo4j


def flatten_json(json_obj, prefix=''):
    flattened = {}
    for key, value in json_obj.items():
        new_key = prefix + '.' + key if prefix else key
        if isinstance(value, dict):
            flattened.update(flatten_json(value, new_key))
        else:
            flattened[new_key] = value
    return flattened


def to_neo4j(networkx_graph):
    """Insert the graph into into neo4j"""
    neo4j = connect()
    G = networkx_graph
    nodes_by_id = {}
    for node in G.nodes(data=True):
        node_id = node[1]['@id']
        properties = flatten_json(node[1])
        label = properties.get('@label', properties.get('@value', properties.get('@id', '')))
        # print(properties)
        # print('---------')
        node_type = properties.get('@type', 'Node').title()
        nodes_by_id[node_id] =  Node(node_type, label=label, **properties)
        neo4j.create(nodes_by_id[node_id])

    for edge in G.edges(data=True):
        src = nodes_by_id[edge[0]]
        tgt = nodes_by_id[edge[1]]
        properties = flatten_json(edge[2])
        # print(properties)
        #print('========')
        edge_type = properties.get('@type', properties.get('relationship', 'Edge')).upper()
        rel = Relationship(src, edge_type, tgt, **properties)
        neo4j.create(rel)
    print('Converted to neo4j.')