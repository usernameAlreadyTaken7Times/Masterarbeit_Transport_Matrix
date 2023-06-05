import osmnx as ox
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas

filepath = "C:/Users/86781/PycharmProjects/pythonProject/data/osm/bremen-latest.osm"
G = ox.graph_from_xml(filepath, simplify=True) # from disk.


# # filter graph to retain only certain edge types
# filtr = ['tertiary', 'tertiary_link', 'secondary', 'unclassified']
# e = [(u, v, k) for u, v, k, d in G.edges(keys=True, data=True) if d['highway'] not in filtr]
# G.remove_edges_from(e)
#
# # remove any now-disconnected nodes or subcomponents, then simplify toplogy
# G = ox.utils_graph.get_largest_component(G)
# G = ox.simplify_graph(G)



fig, ax = ox.plot_graph(G, node_color='r')
