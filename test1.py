# import networkx as nx
# import osmnx as ox
# import osmnx.distance as oxd
#
# path = "C:/Users/86781/PycharmProjects/pythonProject/data/osm/hamburg-latest.osm.pbf"
#
# # create a graph from the PBF file
#
# G = ox.graph_from_file(path, network_type='drive')
#
# # get the nearest network node to each point
# orig_node = oxd.nearest_nodes(G, (37.828903, -122.245846))
# dest_node = oxd.nearest_nodes(G, (37.812303, -122.215006))
#
# # how long is our route in meters?
# nx.shortest_path_length(G, orig_node, dest_node, weight='length')




from pyrosm import OSM
from pyrosm import get_data


path = "C:/Users/86781/PycharmProjects/pythonProject/data/osm/hamburg-latest.osm.pbf"
# Pyrosm comes with a couple of test datasets
# that can be used straight away without
# downloading anything
# fp = get_data("test_pbf")

# Initialize the OSM parser object
osm = OSM(path)


boundaries = osm.get_boundaries()
# boundaries.plot(facecolor="none", edgecolor="blue")

buildings1 = osm.get_buildings()

# Get the borough of Camden as our bounding box
bounding_box = osm.get_boundaries(name="Kreis Segeberg")

bbox_geom = bounding_box['geometry'].values[0]
osm = OSM(path, bounding_box=bbox_geom)

# bounding_box = [10.0376700, 53.6003900, 10.0453000, 53.6030300]
# bounding_box.plot()

# Read all drivable roads
# =======================
drive_net = osm.get_network(network_type="driving")
# drive_net.plot()
buildings2 = osm.get_buildings()
# buildings.plot()

