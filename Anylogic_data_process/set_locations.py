import pandas
import os
import random


def set_distributor_location(lon1, lat1, lon2, lat2, file_path, file_sheet, num):
    """This function aims to create several random distributor records in the given .xlsx file.
    """

    # cal center
    lon_cen = (lon1 + lon2) / 2
    lat_cen = (lat1 + lat2) / 2

    # diff
    lon_diff = lon2 - lon1
    lat_diff = lat2 - lat1

    # store list for coordinates
    dis_lon = []
    dis_lat = []

    # set the distributor's coordinates as a random point outside the shop area rectangle,
    # but always within a rectangular area of size 2*lon_diff, 2*lat_diff
    for i in range(num):
        lon_dis = (random.random() - 0.5) * 2 * lon_diff + lon_cen
        lat_dis = (random.random() - 0.5) * 2 * lat_diff + lat_cen
        point_invalid = (lon1 < lon_dis < lon2) and (lat1 < lat_dis < lat2)

        # keeps retry until get a valid point
        while point_invalid:
            lon_dis = (random.random() - 0.5) * 2 * lon_diff + lon_cen
            lat_dis = (random.random() - 0.5) * 2 * lat_diff + lat_cen
            point_invalid = (lon1 < lon_dis < lon2) and (lat1 < lat_dis < lat2)

        # store the coordinates
        dis_lon.append(lon_dis)
        dis_lat.append(lat_dis)

    # delete the old file
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        pass

    # create .xlsx file
    output = pandas.DataFrame(columns=["", "id", "lat", "lon", "address"],
                              index=range(num))
    for row in range(num):
        output.at[row, ""] = int(row)
        output.at[row, "id"] = str("D" + str(row).rjust(3, "0"))
        output.at[row, "lat"] = str(dis_lat[row])
        output.at[row, "lon"] = str(dis_lon[row])
        output.at[row, "address"] = "Example distributor address"  # the address of the random-address
        # distributors are not available

    output.to_excel(file_path, sheet_name=file_sheet, index=False)
    print("New distributor locations written to the .xlsx file.")
    print('----------------------------------------------------')
    return dis_lon[0], dis_lat[0]


def set_vehicle_info(file, sheetname):
    """This function can be used to create a .xlsx file with vehicle capacity and number information.
    This file will be used as a database file for Anylogic program.
    This function's result is the same as the original Anylogic database file.
    No change is made here."""

    num = 2
    # create .xlsx file
    output = pandas.DataFrame(columns=["", "capacity", "number"],
                              index=range(num))
    # original data
    v_cap = [8.5, 14]
    v_num = [10, 4]

    for row in range(num):
        output.at[row, ""] = int(row)
        output.at[row, "capacity"] = float(v_cap[row])
        output.at[row, "number"] = int(v_num[row])

    # save the file
    output.to_excel(file, sheet_name=sheetname, index=False)
    print("Vehicle information written to the .xlsx file.")
    print('----------------------------------------------------')


def set_other_pre_info(lon1, lat1, lon2, lat2, txt_file, dis_data):
    """This function aims to create a .txt file containing the logistic center's coordinates. The geo info is generated
    randomly around the shop area.

    Lon1, lon2, lat1, lat2: the coordinates of the shop area rectangle, lon1<lon2, lat1<lat2
    :param txt_file: the txt file path.
    """

    # create the txt file to store all the geo info
    with open(txt_file, 'w') as f:
        f.write("----------------------------------------------------------------------------\n")
        f.write("The following coordinates may need to be manually input to Anylogic program.\n")
        f.write("-----------------------------------------------------------------------------\n\n")

        # write the geo-info of the store presentation geo coordinates
        f.write(f"Store (presentation):\n")
        f.write(f"\tlon: {str((lon1 + lon2) / 2)}\n\tlat: {str((lat1 + lat2) / 2)}\n\n")

        # write the geo-info of the distributor's presentation geo coordinates
        f.write(f"Distributor (presentation):\n")
        f.write(f"\tlon: {str(dis_data[0])}\n\tlat: {str(dis_data[1])}\n\n")

        # write the geo-info of the vehicles' presentation geo coordinates
        f.write(f"Vehicle (presentation):\n")
        f.write(f"\tlon: {str(dis_data[2])}\n\tlat: {str(dis_data[3])}\n\n")

        f.write("------------------------------------------------------------------------\n\n")

        # the whole map's center
        f.write(f"Map center (presentation):\n")
        f.write(f"\tlon: {str((lon1 + lon2) / 2)}\n\tlat: {str((lat1 + lat2) / 2)}\n\n")
        f.write("------------------------------------------------------------------------\n")

    f.close()
    print("Other parameters, that need to be entered manually, are written to the .txt file.")
    print('----------------------------------------------------')


def set_logistic_center_location(lon1, lat1, lon2, lat2, file_path, file_sheet):
    """This function can be used to generate an .xlsx file with logistic center's location.
    """
    # center coordinates
    shop_center_coord = ((lon1 + lon2) / 2, (lat1 + lat2) / 2)

    # the wildest range of the logistic center's coordinates
    lon_diff = lon2 - lon1
    lat_diff = lat2 - lat1

    # set the logistic center's coordinates as a random point outside the shop area rectangle,
    # but always within a rectangular area of size 2*lon_diff, 2*lat_diff

    lc_lon_temp = (random.random() - 0.5) * 2 * lon_diff + shop_center_coord[0]
    lc_lat_temp = (random.random() - 0.5) * 2 * lat_diff + shop_center_coord[1]

    point_invalid = (lon1 < lc_lon_temp < lon2) and (lat1 < lc_lat_temp < lat2)

    # keeps retry until get a point outside the shop area
    while point_invalid:
        lc_lon_temp = (random.random() - 0.5) * 2 * lon_diff + shop_center_coord[0]
        lc_lat_temp = (random.random() - 0.5) * 2 * lat_diff + shop_center_coord[1]
        point_invalid = (lon1 < lc_lon_temp < lon2) and (lat1 < lc_lat_temp < lat2)

    # create .xlsx file
    output = pandas.DataFrame(columns=["", "id", "lat", "lon", "address"],
                              index=range(1))

    # there is always only one logistic center
    for row in range(1):
        output.at[row, ""] = int(row)
        output.at[row, "id"] = str("L" + str(row).rjust(3, "0"))
        output.at[row, "lat"] = str(lc_lat_temp)
        output.at[row, "lon"] = str(lc_lon_temp)
        output.at[row, "address"] = "Example logictics center address"  # the address of the random-address
        # distributors are not available

    output.to_excel(file_path, sheet_name=file_sheet, index=False)
    print("New logistic center locations written to the .xlsx file.")
    print('----------------------------------------------------')

    # return the logistic center location back for further use
    return lc_lon_temp, lc_lat_temp
