import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas
import os


def get_block_pop(idx, year, data_path='C:/Users/86781/PycharmProjects/pythonProject/data/'):
    """Use the regression analyzing to predict the population in the chosen block in certain year.
    :param int idx: The index(row) of the block in the .csv file,
    :param int year: the year you want to predict,
    :param str data_path: the data path, in which the .csv file is stored,
    :return: the predicted population number in the chosen block, in certain year.
    """
    # For every block in the test area, read the historical data from .csv file and fit with a suitable function.
    filename = 'pop_dsy_merged.csv'

    # check if the file exists or not
    if os.path.exists(data_path + filename):
        pass
    else:
        print('No population density file found. Please run the update program for world population density files.')

    pop_csv = pandas.read_csv(data_path + filename)
    pop_block = np.zeros(21)
    year_block = np.zeros(21)

    for year_temp in range(2000, 2021):
        pop_block[year_temp - 2000] = pop_csv.values[idx][year_temp - 1998]
        year_block[year_temp - 2000] = year_temp

    # Some blocks have very fluctuating population number over time. This can be because policy changes or city
    # construction, which is hard to predict over long time periods. Here the fluctuation rate is set to 20% of
    # the average population number. If the change is more than that value, use another predict algorithm.

    # diff: the difference of max and min data of population
    diff = max(pop_block.max() - pop_block.mean(), pop_block.mean() - pop_block.min())

    def func1(x, k, b):
        return k * x + b

    popt1, pcov1 = curve_fit(func1, year_block, pop_block)

    # max_..., min_...: the max and min data of the fitting graph
    max_pop_data_block = max(popt1[0] * 2000 + popt1[1], popt1[0] * 2020 + popt1[1])
    min_pop_data_block = min(popt1[0] * 2000 + popt1[1], popt1[0] * 2020 + popt1[1])

    if abs(diff - (max_pop_data_block - min_pop_data_block)) / pop_block.mean() <= 0.20:
        # if the fluctuation rate is less than 20%, use regression algorithm directly
        return popt1[0] * year + popt1[1]
    else:
        # if the fluctuation rate is more than 20%, use another algorithm
        # TODO: try to find a better fitting method, now the regression method is still being used
        return popt1[0] * year + popt1[1]


def get_index_in_csv(lon, lat, data_path='C:/Users/86781/PycharmProjects/pythonProject/data/',
                     filename='pop_dsy_merged.csv'):
    """Return a list, which contains all the index in the .csv file corresponding to the given coordinates.
    The given coordinates should be in the form of (min-lon, min-lat)[left-bottom], (max-lon, max-lat)[right-top].
    :param float lon: the longitude of the point
    :param float lat: the latitude of the point
    :param str data_path: the path, in which the merged .csv file is stored
    :param str filename: the filename of the .csv file
    :return: the index(row) for the point in the .csv file
    :rtype: int
    """

    # check if the file exists or not
    if os.path.exists(data_path + filename):
        pass
    else:
        print('No population density file found. Please run the update program for world population density files.')

    pop_csv = pandas.read_csv(data_path + filename)

    # Clean the year population density data for index searching only to raise efficiency. Due to an unclear reason,
    # the deleting process below cannot be done in one code:-( So it has to be done 2 times, neither of these codes
    # should be deleted. (Or a problem of wrong data format will be raised.)
    pop_csv = pop_csv.drop(pop_csv.columns[2:22], axis=1)
    pop_csv = pop_csv.drop(pop_csv.columns[2], axis=1)

    # Coordinates in .csv file are arranged by latitude, so it would be wise to first look for an approximate range.
    # Then inside this range, a binary search is used to quickly locate the indexes with the block coordinates. This
    # will return also an index range, but much precisely. Finally, the up and bottom range of the index is sent into
    # the last function and traverse to find the block, which the point of the given coordinates is in.
    def get_search_lat_list(lat):
        if lat > 55:
            idx = np.arange(0, 60)
        elif lat > 54:
            idx = np.arange(60, 33335)
        elif lat > 53:
            idx = np.arange(33335, 127918)
        elif lat > 52:
            idx = np.arange(127918, 236366)
        elif lat > 51:
            idx = np.arange(236366, 360892)
        elif lat > 50:
            idx = np.arange(360892, 461390)
        elif lat > 49:
            idx = np.arange(461390, 549412)
        elif lat > 48:
            idx = np.arange(549412, 629537)
        elif lat > 47:
            idx = np.arange(629537, 662167)
        return idx

    def binary_search_idx_lat(index, lat, csv):
        left = 0
        right = len(index) - 1
        right_active = False
        left_active = False

        while left <= right:
            mid = (left + right) // 2

            # if the left/right csv cell have the same lat, then return the index directly
            if csv.values[index[mid]][1] == (
                    right_active * csv.values[index[right]][1] + left_active * csv.values[index[left]][1]):
                break

            # find the blocks where the points of input coordinates are in
            if lat > csv.values[index[mid]][1] + 0.004167:
                right = mid - 1
                right_active = True
                left_active = False
            elif lat < csv.values[index[mid]][1] - 0.004167:
                left = mid + 1
                right_active = False
                left_active = True
            elif lat > csv.values[index[mid]][1] - 0.004167 and lat < csv.values[index[mid]][1] + 0.004167:
                break

        # find all blocks with the same latitude
        k_down = index[mid]
        k_up = index[mid]

        # find the top & bottom index with the same lat
        while csv.values[k_down][1] == csv.values[index[mid]][1]:
            k_down = k_down - 1
        while csv.values[k_up][1] == csv.values[index[mid]][1]:
            k_up = k_up + 1

        return k_down + 1, k_up - 1

    def search_idx_lon(idx_min, idx_max, lon, csv):
        # the longitudes are not arranged by order, so a traverse is unavoidable
        for idx_temp in range(idx_min, idx_max + 1):
            if lon > csv.values[idx_temp][0] - 0.004167 and lon < csv.values[idx_temp][0] + 0.004167:
                break
        return idx_temp

    # TODO: how to catch exceptions when a set of coordinates cannot be found in the .csv file?
    # first use the existing lat dictionary to determine a basic range of the indexes
    index = get_search_lat_list(lat)

    idx_min, idx_max = binary_search_idx_lat(index, lat, pop_csv)
    idx = search_idx_lon(idx_min, idx_max, lon, pop_csv)
    return idx


def get_area_blocks_idx(lon_min, lat_min, lon_max, lat_max, csv_file):
    """Use the input longitude and latitude, find all related blocks' index.
    :param lon_min: The minimum longitude of the points,
    :param lat_min: the minimum latitude of the points,
    :param lon_max: the maximum longitude of the points,
    :param lat_max: the maximum latitude of the points,
    :return: three lists of block indexes, corresponding to area 0,1 and 2."""

    # input the coordinates to find their index in .csv file
    pmin_idx = get_index_in_csv(lon_min, lat_min)
    pmax_idx = get_index_in_csv(lon_max, lat_max)

    filepath = csv_file
    # TODO: after test delete
    filepath = "C:/Users/86781/PycharmProjects/pythonProject/data/pop_dsy_merged.csv"

    # print the block geo-information, which the points are in
    csv = pandas.read_csv(filepath)
    # cut the population data to raise efficiency
    csv = csv.drop(csv.columns[2:22], axis=1)
    csv = csv.drop(csv.columns[2], axis=1)

    print('Points: ', csv.values[pmin_idx][0], csv.values[pmin_idx][1], csv.values[pmax_idx][0], csv.values[pmax_idx][1])

    # calculate how many blocks are involved in area 0
    span_lon = round((csv.values[pmax_idx][0] - csv.values[pmin_idx][0]) / 0.008333) + 1
    span_lat = round((csv.values[pmax_idx][1] - csv.values[pmin_idx][1]) / 0.008333) + 1

    # Here, different test areas will be determined.
    # Area 0 is the square, in which all the shops are located; Note: it also contains blocks with no shop in it.
    # Area 1 is the outer region. People and shops inside area 1 will be counted for simulation.
    # Area 2 is the more outer region. In this area, only the shops will be counted.
    area_1_add = int(0.15 * (span_lat + span_lon) / 2)
    area_2_add = int(0.20 * (span_lat + span_lon) / 2)

    # set the min outer regions of the test area 1 & 2, here are set to 3km and 2km
    if area_1_add <= 3:
        area_1_add = 3
    if area_2_add <= 1:
        area_2_add = 2

    # store list init
    area_0_list = []
    area_1_list = []
    # Area_2 is not 100% necessarily calculated here, because the population predicting process does not have to use the
    # population data from here. So in the future, if the efficiency is not good enough, the code here and in the
    # following loops about area_2 can be discarded.
    area_2_list = []


    print('a, b:', span_lon, span_lat)
    print('area1, area2:', area_1_add, area_2_add)
    print('------------------------------------------------------------------------')

    # use loops to get all needed blocks' indexes, p_min coordinates(0,0)
    for lon_count in range(-(area_1_add+area_2_add), span_lon + area_1_add + area_2_add + 1):
        for lat_count in range(-(area_1_add+area_2_add), span_lat + area_1_add + area_2_add + 1):

            # calculate the block coordinates
            block_lon = lon_min + lon_count * 0.008333
            block_lat = lat_min + lat_count * 0.008333
            ID_block = get_index_in_csv(block_lon, block_lat)

            # print the interim result, for test only
            print('Geo coordinates: ', block_lon, block_lat)
            print('Cartesian coordinates:', lon_count, lat_count)
            print('ID:', ID_block)

            # check if the block is in area 2
            if lon_count < -area_1_add or lon_count > span_lon + area_1_add - 1 or\
                    lat_count < -area_1_add or lat_count > span_lon + area_1_add - 1:
                area_2_list.append(ID_block)
                print('Block in area 2.')
            # check if the block is in area 0
            elif lon_count >= 0 and lon_count < span_lon and lat_count >= 0 and lat_count < span_lat:
                area_0_list.append(ID_block)
                print('Block in area 0.')
            # otherwise, the block is in area 1
            else:
                area_1_list.append(ID_block)
                print('Block in area 1.')
            print('---------------------------------------------------------------------')

    print('test end.')
    # return 0
    pass

def get_test_area_info(lon1, lat1, lon2, lat2, year):
    """This function is used to gather information of the test area base on the regression of historical data.
    :param lon1: The minimum longitude of the points,
    :param lat1: the minimum latitude of the points,
    :param lon2: the maximum longitude of the points,
    :param lat2: the maximum latitude of the points,
    :param year: the year of the to-predict area.
    """

