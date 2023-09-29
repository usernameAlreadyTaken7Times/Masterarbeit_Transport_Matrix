import os.path

from IO.excel_input import load_excel


def get_test_area_customer_shop_possibility_from_xlsx(shop_list_idx, shop_idx, block_idx, block_idx_sum,
                                                      dis_xlsx, dis_sheet,
                                                      shop_xlsx="C:/Users/86781/PycharmProjects/pythonProject/data"
                                                      "/test_area_shops.xlsx",
                                                      shop_sheet="stores"):
    """This function can be used to calculate the possibility of a certain customer on a certain block visiting a
    certain shop.
    :param int shop_list_idx: the index of the chosen shop in the former shop attraction list,
    :param str shop_xlsx: the path string of the .xlsx file containing the shops in the test area, should in the format
    of "lon-lat-address-building_area-etc", in which the shop longitude, shop latitude and shop attraction data can be
    found,
    :param str shop_sheet: the sheet name of the corresponding .xlsx file,
    :return: the possibility of the customer visiting the chosen shop
    """

    # load .xlsx file
    xls = load_excel(shop_xlsx, shop_sheet)
    dis = load_excel(dis_xlsx, dis_sheet)

    # para init
    para_shop = 0
    para_all_shop = 0

    # use loop to read coordinates and attraction info from .xlsx file and calculate the possibility
    for shop_num in range(0, len(xls)):

        if shop_num == shop_list_idx:
            para_shop = (pow(float(xls.values[shop_num][5]), 1) /
                         pow(float(dis.values[(shop_idx-1)*(block_idx_sum)+block_idx][3]), 2))

        # calculate the whole possibility of shop attractions
        para_all_shop += (pow(float(xls.values[shop_num][5]), 1) /
                          pow(float(dis.values[(shop_num-1)*(block_idx_sum)+block_idx][3]), 2))

    return para_shop / para_all_shop


# # test code
# a = get_test_area_customer_shop_possibility(1.1, 2.2, 3)
# pass
