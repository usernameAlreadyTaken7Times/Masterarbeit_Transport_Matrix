import os.path

from IO.excel_input import load_excel
from osm_object_Methods.get_route_distance import get_route_distance
from algorithm.calc_shop_attraction import get_shop_attraction


def get_test_area_customer_shop_possibility(block_cen_lon, block_cen_lat,
                                            shop_list_idx,
                                            shop_xlsx="C:/Users/86781/PycharmProjects/pythonProject/data"
                                                      "/test_area_shops.xlsx"):
    """This function can be used to calculate the possibility of a certain customer on a certain block visiting a
    certain shop.
    :param float block_cen_lon: The longitude of the block center, which the customer is on,
    :param float block_cen_lat: the latitude of the block center, which the customer is on,
    :param int shop_list_idx: the index of the chosen shop in the former shop attraction list,
    :param str shop_xlsx: the path string of the .xlsx file containing the shops in the test area, should in the format
    of "lon-lat-address-building_area-etc", in which the shop longitude, shop latitude and shop attraction data can be
    found,
    :return: the possibility of the customer visiting the chosen shop
    """

    # check the input format
    if isinstance(block_cen_lon, float) and isinstance(block_cen_lat, float) and \
            isinstance(shop_xlsx, str) and isinstance(shop_list_idx, int) and os.path.exists(shop_xlsx):
        pass
    else:
        print('Input error. Please check your input and retry.')
        return 0

    # load .xlsx file
    xls = load_excel(shop_xlsx, "stores")

    # para init
    para_shop = 0
    para_all_shop = 0

    # use loop to read coordinates and attraction info from .xlsx file and calculate the possibility
    for shop_num in range(0, len(xls)):

        if shop_num == shop_list_idx:
            para_shop = pow(xls.values[shop_num][3], 1) / \
                        pow(get_route_distance(block_cen_lon, block_cen_lat, xls.values[shop_num][0], xls.values[shop_num][1]), 2)

        # calculate the whole possibility of shop attractions
        para_all_shop += (pow(xls.values[shop_num][3], 1) /
                          pow(get_route_distance(block_cen_lon, block_cen_lat, xls.values[shop_num][0], xls.values[shop_num][1]), 2))

    return para_shop / para_all_shop

# # test code
# a = get_test_area_customer_shop_possibility(1.1, 2.2, 3)
# pass
