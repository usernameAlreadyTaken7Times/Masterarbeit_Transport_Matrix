import pandas
import os
from math import radians, sin, cos, sqrt, atan2


def haversine(lon1, lat1, lon2, lat2):
    """This function uses haversine formula to calculate the distance from given coordinates
    and return the length (in meters) between two points whose geo-coordinates are already known.
    :param float lon1: The longitude of point 1,
    :param float lat1: the latitude of point 1,
    :param float lon2: the longitude of point 2,
    :param float lat2: the latitude of point 2,
    :rtype float
    :return: the length between two points in kilometer.
    """

    # approximate radius of earth in km
    R = 6373.0

    # Convert coordinate angles to radians
    lon1_r = radians(lon1)
    lat1_r = radians(lat1)
    lon2_r = radians(lon2)
    lat2_r = radians(lat2)

    # calculate the coordinates' difference
    diff_lon = lon2_r - lon1_r
    diff_lat = lat2_r - lat1_r

    a = sin(diff_lat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(diff_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c * 1000


def Anyliogic_output_csv_process(file_path, file_name):
    """This function aims to process the output .csv file from Anylogic model.
    :param str file_path: The .csv file path, which contains Anylogic model's running result,
    :param str file_name: the .csv file's name.
    """

    # check if the file exists
    if os.path.exists(file_path + file_name):
        pass
    else:
        print("Anylogic Model output file does not exist. Please check and retry.")

    csv = pandas.read_csv(file_path + file_name)

    # Please note: because of the different system region and format settings, there could be a format problem in
    # the Anylogic output .csv file: the pandas could have recognition errors.
    # In such case, a manually check before running this process program is necessary.

    for index_num in range(len(csv)):

        # test if reach the last record of a specific vehicle
        id_last_one = False

        if index_num != len(csv):
            if csv.values[index_num][0] != csv.values[index_num+1][0]:
                id_last_one = True

        if not id_last_one:
            pass
            # xp = haversine(csv.values[index_num][5], csv.values[index_num][4],
            #                csv.values[index_num+1][5], csv.values[index_num+1][4]) / 60
        else:
            pass



    pass


# test code
Anyliogic_output_csv_process("C:/Users/86781/PycharmProjects/Distribution Model/Rewe Distribution/",
                             "outputFile.csv")
pass
