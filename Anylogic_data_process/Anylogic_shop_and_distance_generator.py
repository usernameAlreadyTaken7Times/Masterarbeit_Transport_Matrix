import sys
import osmnx as ox
import networkx as nx
from osmnx import graph_from_xml
from multiprocessing import cpu_count, Pool, Manager
import shutil
import pandas
import os
from alternative_Nominatim.get_shop_list_Nominatim import get_shop_list_Nominatim

from settings.Anylogic_related_settings import Anylogic_related_settings
from osm_object_Methods.osm_extract_from_pbf import osm_extract_from_pbf
# from Anylogic_data_process.Nominatim_to_Anylogic_shop import Nominatim_to_Anylogic_shop
from Anylogic_data_process.set_locations import *



def Nominatim_to_Anylogic_shop(lon1, lat1, lon2, lat2, file_path, file_name, file_sheet, shop_file, shop_file_sheet):
    """This function can be used to transform the result of Nominatim query to the format of
    the Anylogic-inputted shop_location list, which is in the form of num-id-lat-lon-address format.
    This file aims to create an Anylogic-program-format shop database and then used as
    :param lon1: the longitude of point 1,
    :param lat1: the latitude of point 1,
    :param lon2: the longitude of point 2,
    :param lat2: the latitude of point 2,
    :param file_path: the path of Nominatim result file,
    :param file_name: the name of Nominatim result file,
    :param file_sheet: the sheet name of Nominatim result file,
    :param shop_file: the path and name of the shop location .xlsx file,
     which is used as the database file for Anylogic program,
    :param shop_file_sheet: the sheet name of the shop location .xlsx file,
    which is used as the database file for Anylogic program.
    """

    # use online server and retrieve the results
    get_shop_list_Nominatim(lon1, lat1, lon2, lat2, "nominatim.openstreetmap.org",
                            file_path, file_name, file_sheet, 1)
    shop_list = pandas.read_excel(file_path + file_name, sheet_name=file_sheet)

    # delete the result file
    os.remove(file_path + file_name)

    # format the Anylogic database .xlsx file
    new_location = pandas.DataFrame(columns=["", "id", "lat", "lon", "address"], index=range(len(shop_list)))

    if len(shop_list) <= 999:
        pass
    else:
        print("Too much results.")
        raise ValueError

    # write data
    for row in range(len(shop_list)):
        new_location.at[row, ""] = int(row)
        new_location.at[row, "id"] = str("S" + str(row).rjust(3, "0"))
        new_location.at[row, "lat"] = float(shop_list.values[row][1])
        new_location.at[row, "lon"] = float(shop_list.values[row][0])
        new_location.at[row, "address"] = str(shop_list.values[row][2])

    new_location.to_excel(shop_file, sheet_name=shop_file_sheet, index=False)
    print("New shop locations written to the .xlsx file.")
    print("---------------------------------------------")


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
    # you can CHANGE the coordinates here!!!
    lon_1 = 10.7276
    lat_1 = 52.7235
    lon_2 = 10.7528
    lat_2 = 52.7325

    config = Anylogic_related_settings

    # generate the shop location .xlsx file
    Nominatim_to_Anylogic_shop(lon_1, lat_1, lon_2, lat_2,
                               config.Nominatim_shop_list_path,
                               config.Nominatim_shop_list_name,
                               config.Nominatim_shop_list_sheet,
                               config.shop_file,
                               config.shop_file_sheet)

    # set the distributor's location
    distributor_num = 1  # you can CHANGE the distributor's number here

    # generate the distributor location .xlsx file,
    # and store the presentation coordinates of a distributor for further use
    dis_pre_lon, dis_pre_lat = set_distributor_location(lon_1, lat_1, lon_2, lat_2,
                                                        config.distributors_file,
                                                        config.distributors_file_sheet, distributor_num)

    # then use this script's code to generate the corresponding distance database
    list_coord, list_ori, list_dest = Anylogic_distance_gernerator(config.OSM_TOOL_PATH,
                                                                   config.pbf_path,
                                                                   config.pbf_name,
                                                                   config.osm_path,
                                                                   config.osm_name,
                                                                   config.distributors_file,
                                                                   config.distributors_file_sheet,
                                                                   config.shop_file,
                                                                   config.shop_file_sheet,
                                                                   config.distance_file)

    # create the distance database with multiprocessing
    cpu_num = cpu_count()

    # read the osm file and store it as a graph for further distance calculating
    G = graph_from_xml(config.osm_path + config.osm_name)

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
    output.to_excel(config.distance_file,
                    sheet_name=config.distance_file_sheet,
                    index=False)

    print("Distance database file generated.")
    print('----------------------------------------------------')
    # end creating distance database

    # delete the unneeded .osm file
    if os.path.exists(config.osm_path + config.osm_name):
        os.remove(config.osm_path + config.osm_name)

    # generate a vehicle information .xlsx file (always unchanged ones)
    set_vehicle_info(config.v_info_file, config.v_info_sheet)

    # generate a logistic center's coordinates in an .xlsx file
    lc_lon, lc_lat = set_logistic_center_location(lon_1, lat_1, lon_2, lat_2,
                                                  config.lc_info_file,
                                                  config.lc_info_sheet)

    # and also write some presentation-relevant geo data in the .txt file
    pre_dis_data = [dis_pre_lon, dis_pre_lat, lc_lon, lc_lat]
    set_other_pre_info(lon_1, lat_1, lon_2, lat_2, config.other_info_txt_file, pre_dis_data)

    # till now, all six .xlsx shops are generated, which are essential to the Anylogic program.
    print('----------------------------------------------------------------------------------')
    print("All six needed file generated. Copying the file to the new Anylogic file folder.")
    print('----------------------------------------------------------------------------------')

    # create a duplication in the new Anylogic program file
    shutil.copy(config.distributors_file, config.distributors_file_new)
    shutil.copy(config.distance_file, config.distance_file_new)
    shutil.copy(config.v_info_file, config.v_info_file_new)
    shutil.copy(config.lc_info_file, config.lc_info_file_new)
    shutil.copy(config.other_info_txt_file, config.other_info_txt_file_new)

    print('----------------------------------------------------------------------------------')
    print("Copy completed. You may run the calculating program now.")
    print('----------------------------------------------------------------------------------')

    # Please note: for the new Anylogic program, the "location.xlsx" file is not needed,
    # but the "locations_with_good_weight.xlsx" file.
    # This file is generated from the "location.xlsx" file in the original Anylogic program folder.
    # So in the copying process, this file should not be copied.

    # This script contains error in multiprocessing.
    # If you stop the program here, all outputs are proceeded without errors.
    sys.exit()
