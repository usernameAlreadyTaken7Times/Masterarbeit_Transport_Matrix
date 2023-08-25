from alternative_Nominatim.get_shop_list_Nominatim import get_shop_list_Nominatim
from Anylogic_data_process.Anylogic_distance_settings import *
import pandas
import os


def Nominatim_to_Anylogic_shop(lon1, lat1, lon2, lat2, file_path, file_name, file_sheet):
    """This function can be used to transform the result of Nominatim query to the format of
    the Anylogic-inputted shop_location list, which is in the form of num-id-lat-lon-address format.

    """

    # use online server and retrieve the results
    get_shop_list_Nominatim(lon1, lat1, lon2, lat2, "nominatim.openstreetmap.org",
                            file_path, file_name, file_sheet, 1)
    shop_list = pandas.read_excel(file_path + file_name, sheet_name=file_sheet)

    # delete the result file
    os.remove(file_path + file_name)

    # reformat the file


    pass


# test code
Nominatim_to_Anylogic_shop(10.5858, 51.7162, 10.6367, 51.7346,
                           Anylogic_distance_settings.Nominatim_shop_list_path,
                           Anylogic_distance_settings.Nominatim_shop_list_name,
                           Anylogic_distance_settings.Nominatim_shop_list_sheet)
pass
