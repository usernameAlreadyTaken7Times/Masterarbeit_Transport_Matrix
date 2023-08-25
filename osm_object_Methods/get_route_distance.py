from osmnx import graph_from_bbox
from osmnx import graph_from_xml
import osmnx as ox
import networkx as nx

import os
os.environ['USE_PYGEOS'] = '0'


def get_route_distance(osm_file, block_cen_lon, block_cen_lat, shop_lon, shop_lat):
    """This function is used to calculate the driving distance and its corresponding driving time between the test
    areas' block's center and to be tested shop. The driving time is calculated with an average speed of 40km/h.
    :param str osm_file: The path and name of the .osm file, which contains the test area's data,
    :param float block_cen_lon: the longitude of the block's center,
    :param float block_cen_lat: the latitude of the block's center,
    :param float shop_lon: the longitude of the shop's center,
    :param float shop_lat: the latitude of the shop's center,
    :return: the driving distance and driving time for the distance, units of measurement meter and second
    """

    '''
    # these code blocks are used for test: compare for the local .osm file and online resource
    xmin, xmax = 10.46843, 10.53718
    ymin, ymax = 52.25082, 52.27246
    # When use the online service to generate a map for route-distance calculating, bounding box is necessary.
    G = graph_from_bbox(ymax, ymin, xmin, xmax, network_type='drive', simplify=True)
    '''

    # check if the .osm file exists
    if os.path.exists(osm_file):
        pass
    else:
        print('.osm File does not exist. Please check your input.')
        return 0

    # load the osm file
    G = graph_from_xml(osm_file)

    orig = (block_cen_lon, block_cen_lat)
    dest = (shop_lon, shop_lat)

    # get the nodes closest to the points in the osm file
    origin_node = ox.nearest_nodes(G, Y=orig[1], X=orig[0])
    destination_node = ox.nearest_nodes(G, Y=dest[1], X=dest[0])

    '''
    # in case of the need of a graph
    shortest_route_by_distance = ox.shortest_path(G, origin_node, destination_node, weight='length')
    fig, ax = ox.plot_graph_route(G, shortest_route_by_distance, route_colors=['r'], route_linewidth=6, node_size=0)
    '''

    # the driving distance in meters
    distance = nx.shortest_path_length(G, origin_node, destination_node, weight='length')
    # print(f"The driving distance is {distance} meters.")

    # make sure the distance is always not 0, because the distances are used as denominators in the following steps
    if distance == 0 or distance == 0.0:
        # here just set minimum distance as 0.3m
        distance = 0.3

    # the driving time between these two points
    time = distance * 3.6 / 40
    # print(f "The driving time is {time} seconds.")

    return distance, time
