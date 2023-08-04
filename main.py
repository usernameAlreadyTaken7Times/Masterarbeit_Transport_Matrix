import sys

# settings
from settings.conf import *

# functions of the subprogram
from IO.excel_input import *
from IO.excel_pre_processing import get_pre_processing_excel
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
from algorithm.get_test_area_retail_day_correction import get_test_area_retail_day_correction

# update programs
from update.PBF_update import pbf_update_program
from update.PBF_update import pbf_Europe_update_program
from update.World_pop_update import POP_update_program


if __name__ == '__main__':

    # TODO: Explain the whole program
    """
    This program aims to estimate the shipment of shops in a given .xlsx file. 
    """

    # Prepare with the configration file: read config file and store the paths for the file and scripts.
    if Production_Env:
        config = Production_Env
    else:
        print('Configuration is not available. Please check again.')
        raise FileNotFoundError

    # ------------------------------clean unneeded files and test if important files exist------------------------------

    # remove the existing .osm file and shop list generated from Nominatim server,
    # which are likely to be from the last simulation
    if os.path.exists(config.DATA_PATH + config.OSM_NAME):
        os.remove(config.DATA_PATH + config.OSM_NAME)

    if os.path.exists(config.DATA_PATH + config.test_area_shop_list_name):
        os.remove(config.DATA_PATH + config.test_area_shop_list_name)

    # check if needed data files exist, first the three data files, which can only be imported, not updated by program
    if os.path.exists(config.DATA_PATH + config.MONTH_file_name) and \
            os.path.exists(config.DATA_PATH + config.INFLATION_file_name) and \
            os.path.exists(config.DATA_PATH + config.BIP_file_name):
        pass
    else:
        print("Key data files (.xlsx) missing. Please check /data folder.")
        raise FileNotFoundError

    # then check weather the population density file and the .pbf file is ready
    if os.path.exists(config.DATA_PATH + config.POP_DEN_file_name):
        pop_den_file_need_update = False
    else:
        pop_den_file_need_update = True

    if os.path.exists(config.PBF_PATH + config.PBF_WHOLE_NAME):
        pbf_file_need_update = False
    else:
        pbf_file_need_update = True

    # at last check if the original input .xlsx file is ready, which contains the original shop list
    if os.path.exists(config.ORG_XLSX_PATH + config.ORG_XLSX_NAME):
        pass
    else:
        print("Please check the input .xlsx file containing the to-be-calculated shops.")
        raise FileNotFoundError

    # ------------------------------------------update program----------------------------------------------------------

    # Prepare phrase: check the .pbf and population density files are updated or not.
    # The update process will only start if the file does not exist,
    # or if the update is required in the configuration file.
    if config.UPDATE_PBF or pbf_file_need_update:
        pbf_update_program(config.PBF_PATH)

    if config.UPDATE_DST or pop_den_file_need_update:
        POP_update_program(config.POP_DEN_store_path, config.POP_DEN_file_path, config.POP_DEN_file_name)

    # ------------------------------------------main program------------------------------------------------------------

    # First, check the input .xlsx file format.
    # Here an extra function is provided for the situation that the coordinates of the shops are not available.

    # read the population density file
    pop_csv = pandas.read_csv(config.DATA_PATH + config.POP_DEN_file_name)

    # pre-process the provided .xlsx file containing shop coordinates and addresses
    get_pre_processing_excel(config.ORG_XLSX_PATH, config.ORG_XLSX_NAME, config.ORG_XLSX_SHEET,
                             config.input_xlsx_file_path, config.input_xlsx_file_name,
                             config.input_xlsx_file_sheet)

    # read the input .xlsx shop file
    input_shop_xlsx = load_excel(config.input_xlsx_file_path + config.input_xlsx_file_name,
                                 config.input_xlsx_file_sheet)

    # loop the input .xlsx file to find the minimum and maximum coordinates of the shops
    lon_min = min([float(input_shop_xlsx.values[i][0]) for i in range(len(input_shop_xlsx))])
    lon_max = max([float(input_shop_xlsx.values[i][0]) for i in range(len(input_shop_xlsx))])
    lat_min = min([float(input_shop_xlsx.values[i][1]) for i in range(len(input_shop_xlsx))])
    lat_max = max([float(input_shop_xlsx.values[i][1]) for i in range(len(input_shop_xlsx))])

    # determine the test area based on the provided coordinates and also get the people number on test area 0&1
    area_info = get_test_area_info(lon_min, lat_min, lon_max, lat_max, config.YEAR, config.TEST_MODE,
                                   config.POP_DEN_file_path + config.POP_DEN_file_name)

    # store the whole people in test area 0&1, for further use
    area_people = sum(area_info[5]) + sum(area_info[11])

    # get the boundary for test area 2, in order to use the boundary data to extract an .osm file from .pbf file
    # use 0.008 as buffer zone to make sure all shops and map roads can be found in the extracted .osm file
    test_area_lon_min = min(area_info[13]) - 0.008
    test_area_lon_max = max(area_info[13]) + 0.008
    test_area_lat_min = min(area_info[14]) - 0.008
    test_area_lat_max = max(area_info[14]) + 0.008

    # extract the test area .osm file from .pbf file
    try:
        osm_extract_from_pbf(test_area_lon_min, test_area_lat_min, test_area_lon_max, test_area_lat_max,
                         config.OSM_TOOL_PATH, config.PBF_PATH, config.PBF_WHOLE_NAME,
                         config.DATA_PATH, config.OSM_NAME)
    except AttributeError:
        print("The input boundary of test area is out of Germany.")
        if config.ALLOW_EUROPE_PBF_UPDATE:
            temp_allow_update_europe_map = input("Do you want to download Europe's .pbf file for that? 0=No, 1=Yes.")
            if temp_allow_update_europe_map == 1:

                # download new europe's .pbf file from server
                pbf_Europe_update_program(config.PBF_PATH)
                print("Trying to extract .osm file with the .pbf file containing all Europe's data.")
                try:
                    # retry extracting the test area's info
                    osm_extract_from_pbf(test_area_lon_min, test_area_lat_min, test_area_lon_max, test_area_lat_max,
                                         config.OSM_TOOL_PATH, config.PBF_PATH, config.PBF_EUROPE_WHOLE_NAME,
                                         config.DATA_PATH, config.OSM_NAME)
                except:
                    print("Attributes error, Calculation ends.")

        else:
            print("Calculation ends.")

    # check if the newly generated .osm file exists
    if os.path.exists(config.DATA_PATH + config.OSM_NAME):
        pass
    else:
        print("Osm file error.")
        raise FileNotFoundError

    # indentify the shops' state using input .xlsx file (here we assume all shops are in the same state)
    state = get_excel_address_state(config.input_xlsx_file_path + config.input_xlsx_file_name,
                                    config.input_xlsx_file_sheet)

    # calculate the average retail sale amount in the shop's state from historical data
    retail_avg = get_retail_average(config.YEAR, state, config.BIP_file_path + config.BIP_file_name,
                                    config.BIP_file_sheet)

    # calculate the retail sale amount of the test area 0 & 1.
    # it should be applied to all shops inside test area 0, 1 & 2 accordingly
    test_area_retail = area_people * retail_avg

    # use different server based on the setting
    if config.Use_online_Nominatim_server:
        Nominatim_server = config.Nominatim_server_online
    else:
        Nominatim_server = config.Nominatim_server_offline

    # use Nominatim service to get a shop list for the whole test area, 0, 1 &2 and write the shop list to an .xlsx file
    try:
        get_shop_list_Nominatim(test_area_lon_min, test_area_lat_min, test_area_lon_max, test_area_lat_max,
                            Nominatim_server, config.test_area_shop_list_path, config.test_area_shop_list_name,
                            config.test_area_shop_list_sheet)
    except:
        print("Test area coordinates are out of range of Germany.")
        # TODO: ERROR type?
        pass
    finally:
        # check if the shop list for the whole test area is available
        if os.path.exists(config.test_area_shop_list_path + config.test_area_shop_list_name):
            pass
        else:
            print("Test area shop list file error.")
            raise FileNotFoundError

    # write the shops' info back into the test area's .xlsx file for further attraction calculation, including shop's
    # building area, the influencing parameters which were analyzed from data of the .osm file
    # at the same time, store the order of the inputted Excel file's shops in test area 0, 1&2 for further use
    shop_order = get_shop_info_osm(test_area_lon_min, test_area_lat_min, config.bounding_box,
                                   config.OSM_PATH + config.OSM_NAME,
                                   config.input_xlsx_file_path + config.input_xlsx_file_name,
                                   config.test_area_shop_list_path + config.test_area_shop_list_name,
                                   config.input_xlsx_file_sheet, config.test_area_shop_list_sheet)

    # shop_order = [1]

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

            print(f"Calculating the customer from {str(block_num+1)}st block to the {str(shop_num+1)}st shop, "
                  f"total {str(len(area_info[1])+len(area_info[7]))} blocks and {str(len(input_shop_xlsx))} shops.")

            # blocks in area 0
            if block_num < len(area_info[1]):
                block_customer = (get_test_area_customer_shop_possibility(
                                        area_info[1][block_num],
                                        area_info[2][block_num],
                                        shop_num_in_excel2,
                                        config.OSM_PATH + config.OSM_NAME,
                                        config.test_area_shop_list_path + config.test_area_shop_list_name,
                                        config.test_area_shop_list_sheet)
                                  * area_info[5][block_num])

            # blocks in area 1
            else:
                block_customer = (get_test_area_customer_shop_possibility(
                                        area_info[7][block_num-len(area_info[1])],
                                        area_info[8][block_num-len(area_info[1])],
                                        shop_num_in_excel2,
                                        config.OSM_PATH + config.OSM_NAME,
                                        config.test_area_shop_list_path + config.test_area_shop_list_name,
                                        config.test_area_shop_list_sheet)
                                  * area_info[11][block_num-len(area_info[1])])

            # add every block's customer together and get the whole customer number of a shop
            customer += block_customer

        shops_customer.append(customer)

    # test if all shop's data written into the list
    if len(shops_customer) == len(input_shop_xlsx):
        pass
    else:
        print("Error.")
        raise ValueError

    # convert the customer number to retail sale amount in Euro
    sale_amount_uncorrected = [i * retail_avg for i in shops_customer]

    # correct the sale amount with yearly inflation and monthly income fluctuation
    sale_amount_temp = [get_test_area_retail_inflation_correction(i,
                                        config.YEAR, config.standard_year,
                                        config.INFLATION_file_path + config.INFLATION_file_name,
                                        config.INFLATION_file_sheet) for i in sale_amount_uncorrected]

    # consider the inflation of buying range between different months
    sale_amount_corrected = [get_test_area_retail_month_correction(i,
                                        config.YEAR, config.MONTH, state,
                                        config.MONTH_file_path + config.MONTH_file_name,
                                        config.MONTH_file_sheet) for i in sale_amount_temp]

    # transform the unit to Euro/day
    sale_amount_corrected_day = get_test_area_retail_day_correction(sale_amount_corrected, config.MONTH, config.YEAR)

    # convert the retail sale amount into retail good weight
    retail_amount = [i * config.RLS_retail for i in sale_amount_corrected_day]

    # write the sale amount back to the input .xlsx file
    add_shop_info_column_to_excel(config.input_xlsx_file_path + config.input_xlsx_file_name,
                                  config.input_xlsx_file_sheet,
                                  retail_amount,
                                  "retail_amount_weight")

    # write the sale amount back to the original .xlsx file in Anylogic program folder
    add_shop_info_column_to_excel(config.ORG_XLSX_PATH + config.ORG_XLSX_NAME,
                                  config.ORG_XLSX_SHEET,
                                  retail_amount,
                                  "retail_amount_weight")

    print("Data written back into the .xlsx file in Anylogic program path, the calculation ends.")

    pass
    sys.exit()
