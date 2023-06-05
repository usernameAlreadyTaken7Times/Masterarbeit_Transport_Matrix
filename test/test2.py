import networkx as nx
import osmnx as ox
import osmnx.distance as oxd

path = "C:/Users/86781/PycharmProjects/pythonProject/data/osm/germany-latest.osm.pbf"

# create a graph from the PBF file

G = ox.graph_from_file(path, network_type='drive')

# get the nearest network node to each point
orig_node = oxd.nearest_nodes(G, (9.9046415, 53.457823))
dest_node = oxd.nearest_nodes(G, (9.9120015, 53.4650054))

# how long is our route in meters?
nx.shortest_path_length(G, orig_node, dest_node, weight='length')