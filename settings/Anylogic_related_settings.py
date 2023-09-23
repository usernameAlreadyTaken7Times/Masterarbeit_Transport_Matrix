class Anylogic_related_settings:

    # the osm tool path, in which the osmium command-line tool's folder is located
    OSM_TOOL_PATH = "C:/Users/86781/anaconda3/Library/bin/"

    # the .pbf file for .osm file extraction
    pbf_path = "C:/Users/86781/PycharmProjects/pythonProject/data/osm/"
    pbf_name = "germany-latest.osm.pbf"

    # --------------------------------------files in the original Anylogic program's path-------------------------------
    # the path for the original Anylogic files
    Anylogic_file_path = "C:/Users/86781/PycharmProjects/Rewe_Distribution_org/"

    # the .osm file store path
    osm_path = Anylogic_file_path
    osm_name = "Anylogic_distance_osm.osm"

    # the file storing the distributor locations
    distributors_file = Anylogic_file_path + "distributor_locations.xlsx"
    distributors_file_sheet = "distributorlocations"

    # the file to store the shop locations
    shop_file = Anylogic_file_path + "locations.xlsx"
    shop_file_sheet = "storelocations"

    # the file to store the generated data of distances between shops and distributors
    distance_file = Anylogic_file_path + "distances.xlsx"
    distance_file_sheet = "distances"

    # the file to store the vehicle information data
    v_info_file = Anylogic_file_path + "v_info.xlsx"
    v_info_sheet = "fleetinfo"

    # the .xlsx file to store the logistic center data
    lc_info_file = Anylogic_file_path + "logistic_center_locations.xlsx"
    lc_info_sheet = "centerlocation"

    # the file to store other geo-info,
    # including the logistics center information data, the shop/distributor/vehicle presentations
    other_info_txt_file = Anylogic_file_path + "pre_info.txt"

    # temp shop list from Nominatim
    Nominatim_shop_list_path = Anylogic_file_path
    Nominatim_shop_list_name = "Nominatim_shops.xlsx"
    Nominatim_shop_list_sheet = "stores"

    # the path and name of the original Anylogic program output .csv files
    csv_org_result_path = Anylogic_file_path
    csv_org_result_name = 'outputFile.csv'

    # --------------------------------------files in the original Anylogic program's path-------------------------------
    # new Anylogic program's path
    Anylogic_file_path_new = "C:/Users/86781/PycharmProjects/Rewe_Distribution_new/"

    # the file storing the distributor locations
    distributors_file_new = Anylogic_file_path_new + "distributor_locations.xlsx"

    # the file to store the generated data of distances between shops and distributors
    distance_file_new = Anylogic_file_path_new + "distances.xlsx"

    # the file to store the vehicle information data
    v_info_file_new = Anylogic_file_path_new + "v_info.xlsx"
    v_info_file_sheet = 'fleetinfo'

    # the .xlsx file to store the logistic center data
    lc_info_file_new = Anylogic_file_path_new + "logistic_center_locations.xlsx"

    # the file to store other geo-info,
    # including the logistics center information data, the shop/distributor/vehicle presentations
    other_info_txt_file_new = Anylogic_file_path_new + "pre_info.txt"

    # the path and name of the new Anylogic program output .csv files
    csv_new_result_path = Anylogic_file_path_new
    csv_new_result_name = 'outputFile.csv'
