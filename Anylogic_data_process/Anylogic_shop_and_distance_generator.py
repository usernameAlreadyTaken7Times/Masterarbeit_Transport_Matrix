import sys
import osmnx as ox
import networkx as nx
from osmnx import graph_from_xml
import pandas
import os
from multiprocessing import cpu_count, Pool, Manager

from settings.Anylogic_related_settings import Anylogic_related_settings
from osm_object_Methods.osm_extract_from_pbf import osm_extract_from_pbf
from Anylogic_data_process.Nominatim_to_Anylogic_shop import Nominatim_to_Anylogic_shop
from Anylogic_data_process.set_locations import *


class cal():
    def __init__(self):
        self.manager = Manager
        self.dis_list = self.manager().list()

    # build a function for route distance calculating in process pool
    def distance_cal(self, G, Arg, num, all_num):
        # argument in the order of G, lon1, lat1, lon2, lat2, id_num

        # append the input coordinates to the nodes in .osm file
        orig = ox.nearest_nodes(G, X=Arg[0], Y=Arg[1])
        dest = ox.nearest_nodes(G, X=Arg[2], Y=Arg[3])

        dis = nx.shortest_path_length(G, orig, dest, weight='length')  # unit in meter
        print(f'{num}. record finishes, total {str(all_num)} records.')
        self.dis_list.append(dis)
        return dis

    def flow(self, G, Arg, cpu_num, loop_num):
        pool = Pool(cpu_num)
        for i in range(loop_num):
            pool.apply_async(self.distance_cal, args=(G, Arg[i], i, loop_num))
        pool.close()
        pool.join()


def Anylogic_distance_gernerator(osm_tool, pbf_path, pbf_name, osm_path, osm_name,
                                 distributor_file, distributor_sheet,
                                 shop_file, shop_sheet,
                                 distance_file):
    """This function aims to use the template and data of distributor and shop locations to generate the distance
     database using local .osm file data. """

    # in this function, skip the file testing. just delete the existing file
    if os.path.exists(distance_file):
        os.remove(distance_file)

    if os.path.exists(osm_path + osm_name):
        os.remove(osm_path + osm_name)

    # read the existing data
    distributor_location = pandas.read_excel(distributor_file, sheet_name=distributor_sheet)
    d_num = len(distributor_location)
    shop_location = pandas.read_excel(shop_file, sheet_name=shop_sheet)
    s_num = len(shop_location)

    # concat the records
    location = pandas.concat([distributor_location, shop_location])

    # set the side coordinates of the shops' area for .osm file extraction
    lon_min_shop = min([float(shop_location.values[i][3]) for i in range(len(shop_location))])
    lon_max_shop = max([float(shop_location.values[i][3]) for i in range(len(shop_location))])
    lat_min_shop = min([float(shop_location.values[i][2]) for i in range(len(shop_location))])
    lat_max_shop = max([float(shop_location.values[i][2]) for i in range(len(shop_location))])

    # the coordinates for distributors
    lon_min_distributor = min([float(distributor_location.values[i][3]) for i in range(len(distributor_location))])
    lon_max_distributor = max([float(distributor_location.values[i][3]) for i in range(len(distributor_location))])
    lat_min_distributor = min([float(distributor_location.values[i][2]) for i in range(len(distributor_location))])
    lat_max_distributor = max([float(distributor_location.values[i][2]) for i in range(len(distributor_location))])

    # use the biggest and smallest coordinates as boundary
    lon_min = min(lon_min_distributor, lon_min_shop)
    lon_max = max(lon_max_distributor, lon_max_shop)
    lat_min = min(lat_min_distributor, lat_min_shop)
    lat_max = max(lat_max_distributor, lat_max_shop)

    # extract .osm file data
    osm_extract_from_pbf(lon_min - 0.008, lat_min - 0.008, lon_max + 0.008, lat_max + 0.008,
                         osm_tool, pbf_path, pbf_name, osm_path, osm_name)

    # test if the .osm file available
    if os.path.exists(osm_path + osm_name) and os.path.getsize(osm_path + osm_name) >= 5000:
        pass
    else:
        raise FileNotFoundError

    list_coord = []
    list_id_ori = []
    list_id_dest = []

    for origin_num in range(d_num + s_num):
        for destination_num in range(d_num + s_num):
            list_coord.append((location.values[origin_num][3], location.values[origin_num][2],
                               location.values[destination_num][3], location.values[destination_num][2]))
            list_id_ori.append(location.values[origin_num][1])
            list_id_dest.append(location.values[destination_num][1])
    return list_coord, list_id_ori, list_id_dest


if __name__ == '__main__':

    # first, use the input coordinates to create a Anylogic program format shop location file
    # please CHANGE the coordinates here!!!
    lon_1 = 11.0029
    lat_1 = 53.1379
    lon_2 = 11.0538
    lat_2 = 53.1557

    # generate the shop location .xlsx file
    Nominatim_to_Anylogic_shop(lon_1, lat_1, lon_2, lat_2,
                               Anylogic_related_settings.Nominatim_shop_list_path,
                               Anylogic_related_settings.Nominatim_shop_list_name,
                               Anylogic_related_settings.Nominatim_shop_list_sheet,
                               Anylogic_related_settings.shop_file,
                               Anylogic_related_settings.shop_file_sheet)

    # set the distributor's location
    distributor_num = 1  # CHANGE
    # generate the distributor location .xlsx file
    set_distributor_location(lon_1, lat_1, lon_2, lat_2,
                             Anylogic_related_settings.distributors_file,
                             Anylogic_related_settings.distributors_file_sheet, distributor_num)

    # then use this script's code to generate the corresponding distance database
    list_coord, list_ori, list_dest = Anylogic_distance_gernerator(Anylogic_related_settings.OSM_TOOL_PATH,
                                                                   Anylogic_related_settings.pbf_path,
                                                                   Anylogic_related_settings.pbf_name,
                                                                   Anylogic_related_settings.osm_path,
                                                                   Anylogic_related_settings.osm_name,
                                                                   Anylogic_related_settings.distributors_file,
                                                                   Anylogic_related_settings.distributors_file_sheet,
                                                                   Anylogic_related_settings.shop_file,
                                                                   Anylogic_related_settings.shop_file_sheet,
                                                                   Anylogic_related_settings.distance_file)

    cpu_num = cpu_count()

    # read the osm file and store it as a graph for further distance calculating
    G = graph_from_xml(Anylogic_related_settings.osm_path + Anylogic_related_settings.osm_name)

    print(f"Total {str(len(list_coord))} records.")

    cal1 = cal()
    cal1.flow(G=G, Arg=list_coord, cpu_num=cpu_num, loop_num=len(list_coord))
    dis = cal1.dis_list

    # build a list for locations:database with a specific order: D-D, D-S, S-D, S-S
    output = pandas.DataFrame(columns=["", "origin", "destination", "distance"],
                              index=range(len(list_coord)))

    for row in range(len(dis)):
        output.at[row, ""] = int(row)
        output.at[row, "origin"] = str(list_ori[row])
        output.at[row, "destination"] = str(list_dest[row])
        output.at[row, "distance"] = float(dis[row] / 1000)

    # generate the distance database .xlsx file
    output.to_excel(Anylogic_related_settings.distance_file,
                    sheet_name=Anylogic_related_settings.distance_file_sheet,
                    index=False)

    # generate a vehicle information .xlsx file (always unchanged one)
    set_vehicle_info(Anylogic_related_settings.v_info_file, Anylogic_related_settings.v_info_sheet)

    # generate a logistic center's (Logistikszentrum) coordinates
    set_logistics_center_info(lon_1, lat_1, lon_2, lat_2, Anylogic_related_settings.lc_info_txt_file)

    # till now, all four .xlsx shops are generated, which are essential to the Anylogic program.
    print("All four needed file generated. Generating program ends.")

    pass
    sys.exit()
