class Anylogic_related_settings:

    # the osm tool path, in which the osmium command-line tool's folder is located
    OSM_TOOL_PATH = "C:/Users/86781/anaconda3/Library/bin/"

    # the .pbf file for .osm file extraction
    pbf_path = "C:/Users/86781/PycharmProjects/pythonProject/data/osm/"
    pbf_name = "germany-latest.osm.pbf"

    # the original path for Anylogic files
    Anylogic_file_path = "C:/Users/86781/PycharmProjects/Distribution_Model/"

    # the .osm file store path
    osm_path = Anylogic_file_path
    osm_name = "Anylogic_distance_osm.osm"

    distributors_file = Anylogic_file_path + "distributor_locations.xlsx"
    distributors_file_sheet = "distributorlocations"

    shop_file = Anylogic_file_path + "locations.xlsx"
    shop_file_sheet = "storelocations"

    # distance_template
    distance_template = Anylogic_file_path + "distances_template.xlsx"
    distance_template_sheet = "distances"

    # the file to store the generated data of distances between shops and distributors
    distance_file = Anylogic_file_path + "distances.xlsx"
    distance_file_sheet = "distances"

    # the file to store the vehicle information data
    v_info_file = Anylogic_file_path + "v_info.xlsx"
    v_info_sheet = "fleetinfo"

    # the file to store the logistics center information data
    lc_info_txt_file = Anylogic_file_path + "ls_info.txt"

    # temp shop list from Nominatim
    Nominatim_shop_list_path = Anylogic_file_path
    Nominatim_shop_list_name = "Nominatim_shops.xlsx"
    Nominatim_shop_list_sheet = "stores"
