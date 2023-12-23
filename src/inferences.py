
def make_inferences(nx_graph):
    print('Making inferences ...')
    graph = nx_graph
    find_parent_relationships(graph)
    create_geometry_relationships(graph)
    return graph

def find_parent_relationships(graph):
    for i in graph.nodes():
        for j in graph.nodes():
            i_node = graph.nodes[i]
            j_node = graph.nodes[j]
            #print(i_node)
            #print('-----')
            if i_node['@id'] == '11':
                print(i_node['@id'])
                print(j_node['@id'])
            if i_node.get('@parent') == j_node.get('@id'):
                graph.add_edge(i, j, relationship='parent', color='red')
                graph.add_edge(j, i, relationship='child', color='red')
                print(f'Added parent/child relationship ({i}) <--> ({j})')


def create_geometry_relationships(graph):
    # Create geometric relationships
    for i in graph.nodes():
        for j in graph.nodes():
            i_node = graph.nodes[i]
            j_node = graph.nodes[j]
            i_x = i_node.get('mxGeometry', {}).get('@x')
            i_y = i_node.get('mxGeometry', {}).get('@y')
            i_width = i_node.get('mxGeometry', {}).get('@width')
            i_height = i_node.get('mxGeometry', {}).get('@height')
            j_x = j_node.get('mxGeometry', {}).get('@x')
            j_y = j_node.get('mxGeometry', {}).get('@y')
            j_width = j_node.get('mxGeometry', {}).get('@width')
            j_height = j_node.get('mxGeometry', {}).get('@height')
            if i_x is None or i_y is None or i_width is None or i_height is None:
                continue
            if j_x is None or j_y is None or j_width is None or j_height is None:
                continue
            x1_lim = (float(i_x), float(i_x) + float(i_width))
            y1_lim = (float(i_y), float(i_y) + float(i_height))
            x2_lim = (float(j_x), float(j_x) + float(j_width))
            y2_lim = (float(j_y), float(j_y) + float(j_height))
            x2_in_x1 = (
                x1_lim[0] < x2_lim[0]
                and x2_lim[1] < x1_lim[1]
            )
            y2_in_y1 = (
                y1_lim[0] < y2_lim[0]
                and y2_lim[1] < y1_lim[1]
            )
            if i == '23' and j == '10':
                print('-'*80)
                print(i_node)
                print(j_node)
                print('X1=', x1_lim, i_x, i_width)
                print('Y1=', y1_lim, i_y, i_height)
                print('X2=', x2_lim, j_x, j_width)
                print('Y2=', y2_lim, j_y, j_height)
                print(x2_in_x1, y2_in_y1)
            if x2_in_x1 and y2_in_y1:
                graph.add_edge(j, i, relationship='in', color='red')
                print(f'Added parent/child relationship ({j}) -[:IN]-> ({i})')
