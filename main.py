import sys
from settings.conf import Production_Env
import os
import pandas

from IO.excel_input import *
from algorithm.calc_test_area_idx_info import *
from osm_object_Methods.osm_extract_from_pbf import *
from algorithm.calc_state_retail_average import get_retail_average
from alternative_Nominatim.get_shop_list_Nominatim import get_shop_list_Nominatim
from osm_object_Methods.get_shop_info_osm import get_shop_info_osm
from algorithm.calc_shop_attraction import get_shop_attraction
from algorithm.get_test_area_customer_shop_possibility import get_test_area_customer_shop_possibility
from algorithm.get_test_area_retail_inflation_correction import get_test_area_retail_inflation_correction
from algorithm.get_test_area_retail_month_correction import get_test_area_retail_month_correction
from osm_object_Methods.get_shop_info_osm import add_shop_info_column_to_excel


if __name__ == '__main__':

    # TODO: main program explanation
    """
    This program aims to 
    """


    # Prepare with the configration file: read config file and store the paths for the file and scripts.
    if Production_Env:
        config = Production_Env
    else:
        print('Configuration is not available. Please check again.')
        raise EOFError

    # ------------------------------------------clean file--------------------------------------------------------------

    # TODO: clean the existing files inside the main path
    pass

    # ------------------------------------------update program----------------------------------------------------------

    # Prepare phrase: check the .pbf and population density files are updated or not.
    # TODO: UPDATE Program
    pass

    # ------------------------------------------main program------------------------------------------------------------

    # First, check the input .xlsx file format.
    # Here an extra function is provided for the situation that the coordinates of the shops are not available.

    # read the population density file
    pop_csv = pandas.read_csv(config.DATA_PATH + config.POP_DEN_file_name)

    # read the input .xlsx shop file
    input_shop_xlsx = load_excel(config.input_xlsx_file_path + config.input_xlsx_file_name,
                                 config.input_xlsx_file_sheet)

    # loop the input .xlsx file to find the minimum and maximum coordinates of the shops
    lon_min = min([float(input_shop_xlsx.values[i][0]) for i in range(len(input_shop_xlsx))])
    lon_max = max([float(input_shop_xlsx.values[i][0]) for i in range(len(input_shop_xlsx))])
    lat_min = min([float(input_shop_xlsx.values[i][1]) for i in range(len(input_shop_xlsx))])
    lat_max = max([float(input_shop_xlsx.values[i][1]) for i in range(len(input_shop_xlsx))])

    # determine the test area based on the provided coordinates and also get the people number on test area 0&1
    area_info = get_test_area_info(lon_min, lat_min, lon_max, lat_max, config.YEAR, config.TEST_MODE)

    # store the whole people in test area 0&1, for further use
    area_people = sum(area_info[5]) + sum(area_info[11])

    # get the boundary for test area 2, in order to use the boundary data to extract an .osm file from .pbf file
    # use 0.008 as buffer zone to make sure all shops and map roads can be found in the extracted .osm file
    test_area_lon_min = min(area_info[13]) - 0.008
    test_area_lon_max = max(area_info[13]) + 0.008
    test_area_lat_min = min(area_info[14]) - 0.008
    test_area_lat_max = max(area_info[14]) + 0.008

    # extract the test area .osm file from .pbf file
    osm_extract_from_pbf(test_area_lon_min, test_area_lat_min, test_area_lon_max, test_area_lat_max,
                         config.OSM_TOOL_PATH, config.PBF_PATH, config.PBF_WHOLE_NAME,
                         config.DATA_PATH, config.OSM_NAME)

    # check if the newly generated .osm file exists
    if os.path.exists(config.DATA_PATH + config.OSM_NAME):
        pass
    else:
        print("Osm file error.")
        raise EOFError

    # indentify the shops' state using input .xlsx file (here we assume all shops are in the same state)
    state = get_excel_address_state(config.input_xlsx_file_path + config.input_xlsx_file_name,
                                    config.input_xlsx_file_sheet)

    # calculate the average retail sale amount in the shop's state from historical data
    retail_avg = get_retail_average(config.YEAR, state, config.BIP_file_path + config.BIP_file_name,
                                    config.BIP_file_sheet)

    # calculate the retail sale amount of the test area 0 & 1.
    # it should be applied to all shops inside test area 0, 1 & 2 accordingly
    test_area_retail = area_people * retail_avg

    # # use different server based on the setting
    # if config.Use_online_Nominatim_server:
    #     Nominatim_server = config.Nominatim_server_online
    # else:
    #     Nominatim_server = config.Nominatim_server_offline
    #
    # # use Nominatim service to get a shop list for the whole test area, 0, 1 &2 and write the shop list to an .xlsx file
    # get_shop_list_Nominatim(test_area_lon_min, test_area_lat_min, test_area_lon_max, test_area_lat_max,
    #                         Nominatim_server, config.test_area_shop_list_path, config.test_area_shop_list_name,
    #                         config.test_area_shop_list_sheet)
    #
    # # check if the shop list for the whole test area is available
    # if os.path.exists(config.test_area_shop_list_path + config.test_area_shop_list_name):
    #     pass
    # else:
    #     print("Test area shop list file error.")
    #     raise EOFError
    #
    # # write the shops' info back into the test area's .xlsx file for further attraction calculation, including shop's
    # # building area, the influencing parameters which were analyzed from data of the .osm file
    # # at the same time, store the order of the inputted Excel file's shops in test area 0, 1&2 for further use
    # shop_order = get_shop_info_osm(test_area_lon_min, test_area_lat_min, config.bounding_box,
    #                                config.OSM_PATH + config.OSM_NAME,
    #                                config.input_xlsx_file_path + config.input_xlsx_file_name,
    #                                config.test_area_shop_list_path + config.test_area_shop_list_name,
    #                                config.input_xlsx_file_sheet, config.test_area_shop_list_sheet)

    shop_order = [1]






    # retrieve the shops' attraction data inside the whole test area 0, 1&2
    test_area_shops_attraction = get_shop_attraction(config.test_area_shop_list_path + config.test_area_shop_list_name,
                                                     config.test_area_shop_list_sheet)

    # the customer number list of the shops
    shops_customer = []

    # loop in every block to calculate the given shop's visiting customer
    for shop_num in range(len(input_shop_xlsx)):

        shop_num_in_excel2 = int(shop_order[shop_num])
        customer = 0

        for block_num in range(len(area_info[1])+len(area_info[7])):

            print(f"Calculating the customer from {str(block_num+1)}st block to the {str(shop_num+1)}st shop,"
                  f" total {str(len(area_info[1])+len(area_info[7]))} blocks and {str(len(input_shop_xlsx))} shops.")

            # blocks in area 0
            if block_num < len(area_info[1]):
                block_customer = get_test_area_customer_shop_possibility(area_info[1][block_num], area_info[2][block_num],
                                                        shop_num_in_excel2, config.OSM_PATH + config.OSM_NAME,
                                                        config.test_area_shop_list_path + config.test_area_shop_list_name,
                                                        config.test_area_shop_list_sheet) * area_info[5][block_num]

            # blocks in area 1
            else:
                block_customer = get_test_area_customer_shop_possibility(area_info[7][block_num-len(area_info[1])],
                                                                         area_info[8][block_num-len(area_info[1])],
                                                                         shop_num_in_excel2, config.OSM_PATH + config.OSM_NAME,
                                                                         config.test_area_shop_list_path + config.test_area_shop_list_name,
                                                                         config.test_area_shop_list_sheet) * area_info[11][block_num-len(area_info[1])]

            # add every block's customer together and get the whole customer number of a shop
            customer += block_customer

        shops_customer.append(customer)

    # test if all shop's data written into the list
    if len(shops_customer) == len(input_shop_xlsx):
        pass
    else:
        print("Error.")
        raise ValueError

    # convert the customer number to retail sale amount
    sale_amount_uncorrected = [i * retail_avg for i in shops_customer]

    # correct the sale amount with yearly inflation and monthly income fluctuation
    sale_amount_temp = [get_test_area_retail_inflation_correction(i, config.YEAR, config.standard_year,
                                                                   config.INFLATION_file_path + config.INFLATION_file_name,
                                                                   config.INFLATION_file_sheet) for i in sale_amount_uncorrected]

    sale_amount_corrected = [get_test_area_retail_month_correction(i, config.YEAR, config.MONTH, state,
                                                               config.MONTH_file_path + config.MONTH_file_name,
                                                               config.MONTH_file_sheet) for i in sale_amount_temp]

    # convert the retail sale amount into retail good weight
    retail_amount = [i * config.RLS_retail for i in sale_amount_corrected]

    # write the sale amount back to the original .xlsx file
    add_shop_info_column_to_excel(config.input_xlsx_file_path + config.input_xlsx_file_name,
                                  config.input_xlsx_file_sheet,
                                  retail_amount,
                                  "retail_amount_weight")

    pass

    # sys.exit()
