import osmnx as ox
import networkx as nx
from osmnx import graph_from_xml
import pandas
import os
from multiprocessing import Process
from multiprocessing import Pool

from Anylogic_data_process.Anylogic_distance_settings import Anylogic_distance_settings
from osm_object_Methods.osm_extract_from_pbf import osm_extract_from_pbf


def Anylogic_distance_gernerator(osm_tool, pbf_path, pbf_name, osm_path, osm_name,
                                 distributor_file, distributor_sheet,
                                 shop_file, shop_sheet,
                                 distance_template, distance_template_sheet,
                                 distance_file, distance_file_sheet):
    """This function aims to use the template and data of distributor and shop locations to generate the distance
     database using local .osm file data. """

    # in this function, skip the file testing. just delete the existing file
    if os.path.exists(distance_file):
        os.remove(distance_file)

    if os.path.exists(osm_path + osm_name):
        os.remove(osm_path + osm_name)

    # read the existing data
    distributor_location = pandas.read_excel(distributor_file, sheet_name=distributor_sheet)
    shop_location = pandas.read_excel(shop_file, sheet_name=shop_sheet)

    # set the side coordinates of the shops' area for .osm file extraction
    lon_min = min([float(shop_location.values[i][3]) for i in range(len(shop_location))])
    lon_max = max([float(shop_location.values[i][3]) for i in range(len(shop_location))])
    lat_min = min([float(shop_location.values[i][2]) for i in range(len(shop_location))])
    lat_max = max([float(shop_location.values[i][2]) for i in range(len(shop_location))])

    # extract .osm file data
    osm_extract_from_pbf(lon_min-0.008, lat_min-0.008, lon_max+0.008, lat_max+0.008,
                         osm_tool, pbf_path, pbf_name, osm_path, osm_name)

    # test if the .osm file available
    if os.path.exists(osm_path + osm_name) and os.path.getsize(osm_path + osm_name) >= 5000:
        pass
    else:
        raise FileNotFoundError

    # read the osm file and store it as a graph for further distance calculating
    G = graph_from_xml(osm_path + osm_name)

    # build a function for route distance calculating in process pool
    def distance_cal(G, lon1, lat1, lon2, lat2):
        # append the input coordinates to the nodes in .osm file
        orig = ox.nearest_nodes(G, X=lon1, Y=lat1)
        dest = ox.nearest_nodes(G, X=lon2, Y=lat2)
        return nx.shortest_path_length(G, orig, dest, weight='length')  # unit in meter

    # build a list for locations:database with a specific order: D-D, D-S, S-D, S-S



    pass


# test code
Anylogic_distance_gernerator(Anylogic_distance_settings.OSM_TOOL_PATH,
                             Anylogic_distance_settings.pbf_path,
                             Anylogic_distance_settings.pbf_name,
                             Anylogic_distance_settings.osm_path,
                             Anylogic_distance_settings.osm_name,
                             Anylogic_distance_settings.distributors_file,
                             Anylogic_distance_settings.distributors_file_sheet,
                             Anylogic_distance_settings.shop_file, Anylogic_distance_settings.shop_file_sheet,
                             Anylogic_distance_settings.distance_template,
                             Anylogic_distance_settings.distance_template_sheet,
                             Anylogic_distance_settings.distance_file,
                             Anylogic_distance_settings.distance_file_sheet)
pass
