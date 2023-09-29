import os
import re
import pandas as pd
import numpy as np

from IO.excel_input import load_excel


def add_shop_info_column_to_excel(input_excel, sheet_name, info_column, info_name):
    """This function aims to write shop data into existing .xlsx file, like shop building area.

    Noted: This function is only programmed to write one column of data for every time.
    If you want to write more than one column of data, please use loops and call this function more times.
    The info list you inputted should have the same length as the data in the original .xlsx file.

    :param str input_excel: The path of the .xlsx file, in which you want to write data,
    :param str sheet_name: the sheet name of the .xlsx file, in which you want to write data,
    :param list, array info_column: an info column of the shop, which you want to write to the Excel file,
    :param str info_name: the name of the info column.

     """
    excel = load_excel(input_excel, sheet_name)
    column = []

    # read all .xlsx file column names
    for column_name in excel.columns.values:
        column.append(column_name)
    column.append(info_name)

    excel_file_temp = pd.DataFrame(columns=column, index=range(len(excel)))
    for row in range(len(excel)):
        for column_num in range(len(excel.columns) + 1):
            if column_num < len(excel.columns):
                excel_file_temp.at[row, column[column_num]] = excel.values[row][column_num]
            elif column_num == len(excel.columns):
                excel_file_temp.at[row, column[column_num]] = info_column[row]

    # write the data back
    excel_file_temp.to_excel(input_excel, sheet_name=sheet_name, index=False)
    print(f'Info {info_name} data column added to .xlsx file.')


def add_shop_record_to_excel(input_excel, sheet_name, info_row_1, info_row_2, info_row_3):
    """This function aims to write one/several shop data record into an existing .xlsx file.

    Noted: This function is only programmed to write one row of data for every time.
    If you want to write more than one column of data, please use loops and call this function more times.
    The three rows of index should be in the same length.

    :param str input_excel: The path of the .xlsx file, in which you want to write data,
    :param str sheet_name: the sheet name of the .xlsx file, in which you want to write data,
    :param list info_row_1: an info row of the shop, which you want to write to the Excel file,
    :param list info_row_2: the second info row of the shop, which you want to write to the Excel file,
    :param list info_row_3: the third info row of the shop, which you want to write to the Excel file.
    """
    excel = load_excel(input_excel, sheet_name)

    # the following code is hard-coded for one row of lon-lat-address format only,
    # so a random length of data is not supported.
    excel_file_temp = pd.DataFrame(columns=["lon", "lat", "address"], index=range(len(excel)+len(info_row_1)))
    for index_row_num in range(len(excel)+len(info_row_1)):
        if index_row_num < len(excel):
            excel_file_temp.at[index_row_num, "lon"] = excel.values[index_row_num][0]
            excel_file_temp.at[index_row_num, "lat"] = excel.values[index_row_num][1]
            excel_file_temp.at[index_row_num, "address"] = excel.values[index_row_num][2]
        else:
            excel_file_temp.at[index_row_num, "lon"] = info_row_1[index_row_num - len(excel)]
            excel_file_temp.at[index_row_num, "lat"] = info_row_2[index_row_num - len(excel)]
            excel_file_temp.at[index_row_num, "address"] = info_row_3[index_row_num - len(excel)]

    # store data
    excel_file_temp.to_excel(input_excel, sheet_name=sheet_name, index=False)
    print(f'{len(info_row_1)} rows of data is added to .xlsx file.')


def get_shop_info_osm_multi_OSM_test(bbox=0.0003,
                      xlsx_file1="C:/Users/86781/PycharmProjects/pythonProject/data/shop_list_coordinates.xlsx",
                      xlsx_file2="C:/Users/86781/PycharmProjects/pythonProject/data/test_area_shops.xlsx",
                      xlsx_file_sheet1="stores", xlsx_file_sheet2="stores"):
    """This function is used to get the shop information from .osm.pbf file, in order to calculate their attractions
     in the following steps. The longitude and latitude should be able to be found in the .xlsx file, which was
     generated before by a script using Nominatim service or an .osm.pbf traversal program.

     Please note: this function is different from the one in script "get_shop_info_osm", because this function only
     returns the order of the shop list as well as several lists with information of the shops.
     Unlike the one in script "get_shop_info_osm", this function does not search for the osm file for shop information.

     :param float bbox: The offset or tolerance of the coordinates, default as 0.0003. In the german region it is
      about 20m in longitude and about 33m in latitude,
     :param str xlsx_file1: the .xlsx file, provided from the very beginning, containing geo-coordinates of the shops in
      area 0, (only the ones whose cargo volume is going to be calculated)
     :param str xlsx_file2: the .xlsx file, generated from former Nominatim script, containing geo-coordinates of the
      shops in area 0,1 and 2,
     :param str xlsx_file_sheet1: the workbook name of xlsx_file1,
     :param str xlsx_file_sheet2: the workbook name of xlsx_file2.
     :return: TBD,
     :rtype: TBD
    """

    # load excel for the shop list in area 0&1&2
    excel_file2 = load_excel(xlsx_file2, xlsx_file_sheet2)

    # load excal for the shop list in area 0
    excel_file1 = load_excel(xlsx_file1, xlsx_file_sheet1)

    # para init
    shop_lon = []
    shop_lat = []
    shop_address = []

    # use loop to read data from excel_file
    for shop_num in range(0, len(excel_file2)):
        shop_lon.append(excel_file2.values[shop_num][0])
        shop_lat.append(excel_file2.values[shop_num][1])
        shop_address.append(excel_file2.values[shop_num][2])

    # extract shop names from the shop_address
    shop_names = []
    for shop_num_1 in range(len(shop_address)):
        shop_names.append(str(shop_address[shop_num_1]).partition(',')[0])

    # -----------------------------extinguish if the shop in the list is in area 0 or in area 1&2---------------------
    area_0_num = []  # shows where the shop in area 0 is in .xlsx file of area 0, 1&2.
    area_0_idc = []  # indicate weather the corresponding position's shop (in area 0) is available the list of 0, 1&2.
    for i in range(0, len(excel_file1)):
        for j in range(0, len(excel_file2)):

            # Transverse to find all coordinates match.

            # Noted: The coordinates should be 100% the same, so in the before steps, a cross-mix of Nominatim and osm
            # searching for the shop list should not be applied,
            # because the coordinates from different methods could contain minor errors
            # that leads to a matching failure.
            # A possible solution is to use tolerance(bounding box) to match the coordinates fuzzily,
            # but it is not fully tested here.
            # Therefore, which value the tolerance should use is still not 100% clear.

            # In this case, a bbox of 0.0003 is applied to find matches.
            # But again, if you are certain that both coordinates were found with the same method (Nominatim or osm),
            # just use '==' and skip the tolerance.

            # Match the shop in excel_1(area 0) to the ones in excel_2(area 0, 1&2).
            # Theoretically, all shops inside excel_1 should be found in excel_2,
            # because excel_2 contains all supermarkets in a bigger area.
            # But if it doesn't, an indicator "area_0_idc" is used to record all shops of excel_1 that are not found
            # here.
            if excel_file2.values[j][0] - bbox / 2 <= excel_file1.values[i][0] <= excel_file2.values[j][0] + bbox / 2 \
                    and excel_file2.values[j][1] - bbox / 3 <= excel_file1.values[i][1] <= excel_file2.values[j][1] + bbox / 3:
                area_0_num.append(j)
                break

            # if it is already the end of excel_2, and still no match is found, then write -1 to area_0_num and write
            # the index of the shop in excel_1 to area_0_idc
            if j == (len(excel_file2) - 1):
                area_0_num.append(-1)
                area_0_idc.append(i)

    # test if the code block has already found all shops in area 0
    if -1 in area_0_num:
        # in this case, area_0_idc is not Null and can be handled directly without testing
        shop_0_unmatched_print = re.findall(r'\d+', str(np.array(area_0_idc)+1))
        shop_print_str = ''
        for num_temp in range(len(shop_0_unmatched_print)):
            shop_print_str = ''.join([shop_print_str, shop_0_unmatched_print[num_temp], ','])

        print(f'The {shop_print_str} shop/shops in area 0 (file 1) are not found in the shop list. '
              f'Will write it/them to shop list for further searching.')

        # write the data record of the missing shop to excel_2
        miss_log_lon = []
        miss_log_lat = []
        miss_log_address = []
        excel_1_order = []  # this list should be used to store the order of the original shops in test area's shop list
        num_temp2 = 0

        # build lists to store the missing shop's data
        for miss_log_num in range(len(area_0_num)):
            if area_0_num[miss_log_num] == -1:
                miss_log_lon.append(excel_file1.values[miss_log_num][0])
                miss_log_lat.append(excel_file1.values[miss_log_num][1])
                miss_log_address.append(excel_file1.values[miss_log_num][2])

                excel_1_order.append(len(excel_file2)+num_temp2)
                num_temp2 += 1
            else:
                excel_1_order.append(area_0_num[miss_log_num])

        # write the records to excel_file_2
        add_shop_record_to_excel(xlsx_file2, xlsx_file_sheet2, miss_log_lon, miss_log_lat, miss_log_address)

    else:
        print('All shops\' coordinates found.')
        excel_1_order = area_0_num

    # --------------------------------extinguish process ends--------------------------------------------------------

    def extract_shop_details(address):
        """This function is used to separate the name, housenumber and street of a shop from its address string.
         Please note: sometimes in the Nominatim server's result, the name or the housenumber is not available. But it
         is assumed that they will not be absent at the same time.
        :param str address: The string of the shop address, containing housenumber, shop name and street at the same
         time.
        """
        if isinstance(address, str):
            pass
        else:
            print('Check your input address string.')
        slt = address.split(', ')

        # postcode index
        post_idx = -1
        for num_temp in range(len(slt) - 3, len(slt)):
            if slt[num_temp].isdigit() and len(slt[num_temp]) == 5:
                post_idx = num_temp

        # housenumber index
        number_idx = -1
        number = None
        for num_temp1 in range(0, post_idx - 2):
            # Some housenumber have one character at the end, like '15a,' '30c',
            # there are also house numbers like '1a/b,' and they are hard to tell.
            # Now this has trouble telling the house numbers and names,
            # when a shop has a name like '5723 Pizza' or '1.Pizza'.
            # This program will think that could be the house number.
            # I have to admit that I do not have any clue how to fix it, now I just assume a housenumber is not longer
            # than 10 characters.

            if slt[num_temp1].isdigit() or slt[num_temp1][0:-1].isdigit() or \
                    (slt[num_temp1][0].isdigit() and len(slt[num_temp1]) <= 10):
                number_idx = num_temp1
                number = slt[num_temp1]
            # in this case, no housenumber is available
            else:
                pass

        # name index
        name_idx = -1
        name = None

        # when the house number is not available or at 2. places, assume the name is available at slt[0]
        if number_idx == -1 or number_idx == 1:
            name = slt[0]
            name_idx = 0
        # if housenumber is at 1. place, name is not available
        elif number_idx == 0:
            pass
        elif number_idx >= 2:
            # before housenumber there are two spots, normally should not happen
            pass

        # street string
        street = None

        # no housenumber available, street is the next spot of name (There exists at least one of name and housenumber)
        if number_idx == -1:
            if name_idx == 0:
                street = slt[name_idx + 1]
            # both name and housenumber is not there(backup)
            else:
                street = slt[0]
        # no name, 1. place:housenumber, 2. place:street
        elif number_idx == 0:
            street = slt[1]
        # name takes more than one place
        else:
            street = slt[number_idx + 1]

        return name, number, street

    # prepare for the input list parameters for function "get_shop_way_ref_osm", which aims to read .osm file as xml
    # format and acquire information from it
    lon_list = []
    lat_list = []
    name_list = []
    housenumber_list = []
    street_list = []

    area_list = []
    infra = []

    # reload the excel_2 to apply the possible former changes to it
    excel_file2 = load_excel(xlsx_file2, xlsx_file_sheet2)

    for shop_num in range(len(excel_file2)):
        lon_list.append(excel_file2.values[shop_num][0])
        lat_list.append(excel_file2.values[shop_num][1])
        name, housenumber, street = extract_shop_details(excel_file2.values[shop_num][2])
        name_list.append(name)
        housenumber_list.append(housenumber)
        street_list.append(street)

    # # get shop list's information (now only building area list)
    # area_list, infra = get_shop_way_ref_osm(lon_list, lat_list, name_list, housenumber_list, street_list, osm_file, bbox, lon_org, lat_org)
    #
    # # store the list with building area and factor data back to the original .xlsx file_2
    # add_shop_info_column_to_excel(xlsx_file2, xlsx_file_sheet2, area_list, 'building_area')
    # add_shop_info_column_to_excel(xlsx_file2, xlsx_file_sheet2, infra, 'infra_factor')
    #
    # print('All shops\' building area stored into the original .xlsx file.')
    return excel_1_order, lon_list, lat_list, name_list, housenumber_list, street_list


# # test code
# get_shop_info_osm(10.46843, 52.25082)
# pass
