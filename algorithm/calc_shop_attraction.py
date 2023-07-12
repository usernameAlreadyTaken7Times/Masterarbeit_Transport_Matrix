import numpy as np
import os
from IO.excel_input import load_excel
from osm_object_Methods.get_shop_info_osm import add_shop_info_column_to_excel

def get_shop_attraction(shop_xlsx="C:/Users/86781/PycharmProjects/pythonProject/data/test_area_shops.xlsx",
                        shop_xlsx_sheet="stores"):
    """This function is used to read the shop list and their relevant information (including building area, etc.) from
    a .xlsx file and calculate the shops' attraction using the law of Attraction and its variants.
    :param str shop_xlsx: The path string of the .xlsx file containing the shops in the test area, should in the format
    of "lon-lat-address-building_area-etc",
    :param str shop_xlsx_sheet: the sheet name.
    """
    if os.path.exists(shop_xlsx):
        pass
    else:
        print('File does not exist. Please check your input .xlsx file.')

    xls = load_excel(shop_xlsx, shop_xlsx_sheet)

    # In this version of script, only shop building area is being calculated, and it is the only parameter that
    # influences the attraction of the shop.
    # In the further versions, more parameters could be added, including shop
    # grades or accessibility.

    attc = np.ones(len(xls))

    # ------------------------------------para area---------------------------------
    # here all parameters should be listed.
    # In this version, only the shop area is listed, and it has a square
    # relationship with the shop attraction.

    area = np.zeros(len(xls))
    factor = np.ones(len(xls))
    k_area = 2

    # ------------------------------------------------------------------------------

    for shop_num in range(0, len(xls)):
        area[shop_num] = xls.values[shop_num][3]
        factor[shop_num] = xls.values[shop_num][4]

        # read other relevant data from .xlsx file

        # calculate the shop attraction
        attc[shop_num] = pow(area[shop_num], k_area) * factor[shop_num]

    add_shop_info_column_to_excel(shop_xlsx, shop_xlsx_sheet, attc, "attraction")

    return attc


# # test code
# a = get_shop_attraction()
# pass
