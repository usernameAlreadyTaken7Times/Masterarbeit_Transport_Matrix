from alternative_Nominatim.get_shop_list_Nominatim import get_shop_list_Nominatim
import pandas
import os
import random


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


# test code
# Nominatim_to_Anylogic_shop(10.5858, 51.7162, 10.6367, 51.7346,
#                            Anylogic_distance_settings.Nominatim_shop_list_path,
#                            Anylogic_distance_settings.Nominatim_shop_list_name,
#                            Anylogic_distance_settings.Nominatim_shop_list_sheet,
#                            Anylogic_distance_settings.shop_file,
#                            Anylogic_distance_settings.shop_file_sheet)
# Nominatim_to_Anylogic_shop(13.3747, 52.5101, 13.4002, 52.5191,
#                            Anylogic_distance_settings.Nominatim_shop_list_path,
#                            Anylogic_distance_settings.Nominatim_shop_list_name,
#                            Anylogic_distance_settings.Nominatim_shop_list_sheet,
#                            Anylogic_distance_settings.shop_file,
#                            Anylogic_distance_settings.shop_file_sheet)
#
# pass
