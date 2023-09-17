import sys
import osmnx as ox
import networkx as nx
from osmnx import graph_from_xml
import pandas
import os
from multiprocessing import Process, cpu_count, Pool, Manager

from settings.program_conf import *




def distance_generator(block_lon_list, block_lat_list,
                       shop_file, shop_file_sheet):
    """This function aims to use the block geo information and the geo data of shops to generate a distance database
     using local .osm file data. """

    # in this function, skip the file testing. just delete the existing file

    # read the existing data
    shop_location = pandas.read_excel(shop_file, sheet_name=shop_file_sheet)
    shop_lon_list = [float(shop_location.values[i][0]) for i in range(len(shop_location))]
    shop_lat_list = [float(shop_location.values[i][1]) for i in range(len(shop_location))]

    list_coord = []
    list_shop = []
    list_block = []

    for origin_num in range(len(shop_lon_list)):
        for destination_num in range(len(block_lon_list)):
            list_coord.append((shop_lon_list[origin_num], shop_lat_list[origin_num],
                               block_lon_list[destination_num], block_lat_list[destination_num]))
            list_shop.append('shop_' + str(origin_num + 1))
            list_block.append('block_' + str(destination_num + 1))
    return list_coord, list_shop, list_block


def distance_writer(shop_list, block_list, distance_list, xlsx_file, xlsx_file_sheet):

    output = pandas.DataFrame(columns=["", "shop", "block", "distance"], index=range(len(shop_list)))

    for row in range(len(distance_list)):
        output.at[row, ""] = int(row + 1)
        output.at[row, "shop"] = str(shop_list[row])
        output.at[row, "block"] = str(block_list[row])
        output.at[row, "distance"] = float(distance_list[row])

    output.to_excel(xlsx_file, sheet_name=xlsx_file_sheet, index=False)
