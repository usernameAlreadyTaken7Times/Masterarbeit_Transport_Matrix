import numpy as np
import os
from IO.excel_input import load_excel


def get_shop_attraction(shop_xlsx):
    """This function is used to read the shop list and their relevant information (including building area, etc.) from
    a .xlsx file and calculate the shops' attraction using the law of Attraction and its variants.
    :param str shop_xlsx: The path string of the .xlsx file containing the shops in the test area, should in the format
    of "lon-lat-address-building_area-etc."
    """
    if os.path.exists(shop_xlsx):
        pass
    else:
        print('File does not exist. Please check your input .xlsx file.')

    xls = load_excel(shop_xlsx)

