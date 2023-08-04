# This is the configuration file of the whole program, storing the file path and other strings.
# If the production and test environments are changed, please change the following corresponding parameters.

class Common_Env(object):

    # --------------------------------common variables------------------------------------------------------------------

    # in test mode?
    # (shorten test area's side length to reduce calculation burden significantly and thus raise efficiency)
    TEST_MODE = True

    # update the .pbf files and population density file before running the program?
    # Please note: when the .pbf files or the people density files do not exist, the update procedure will be triggered.
    UPDATE_PBF = True
    UPDATE_DST = False

    # weather the downloading of the whole Europe's .pbf file is allowed,
    # when the test area's boundary is out of Germany
    ALLOW_EUROPE_PBF_UPDATE = False

    # Nominatim service online?
    Use_online_Nominatim_server = True

    # default Nominatim server
    Nominatim_server_offline = "134.169.70.84"  # the Nominatim server of IMN

    # default online Nominatim server.
    # unless "Use_online_Nominatim_server" is set to False, this server is going to be used
    Nominatim_server_online = "nominatim.openstreetmap.org"

    # the bounding box's side length, default=0.0003
    bounding_box = 0.0003

    # the year of calculation for the program, and should be in range 2000-2025
    YEAR = 2007

    # the month of calculation for the program, and should be in range 1-12 E.g., for August use number 8 rather than 08
    MONTH = 2

    # the standard year for cargo price-cargo volume calculation, and is only used to convert the sales of the
    # current year to the corresponding standard year to exclude the effects of inflation and monthly sales fluctuations
    standard_year = 2005


class Production_Env(Common_Env):

    """
    This is the environment setting for the production process.
    """

    # --------------------------------tools and services----------------------------------------------------------------

    # the osm tool path, in which the osmium command-line tool's folder is located
    OSM_TOOL_PATH = "C:/Users/86781/anaconda3/Library/bin/"

    # --------------------------------data files------------------------------------------------------------------------

    # the anylogic program path, only used to get the input .xlsx file
    ANYLOGIC_PATH = "C:/Users/86781/PycharmProjects/Distribution Model/"

    # original shop .xlsx file path, name and sheet name,
    # which will be read by the program as input
    ORG_XLSX_PATH = ANYLOGIC_PATH
    ORG_XLSX_NAME = "locations.xlsx"
    ORG_XLSX_SHEET = "stores"

    # the main program path
    PROGRAM_PATH = "C:/Users/86781/PycharmProjects/pythonProject/"

    # the data path, in which all program data and files are stored
    DATA_PATH = PROGRAM_PATH + "data/"

    # the folder path, in which all .pbf files are stored
    PBF_PATH = DATA_PATH + "osm/"

    # the .pbf file for the whole Germany
    PBF_WHOLE_NAME = "germany-latest.osm.pbf"

    # the .pbf file for the whole Europe (if available)
    PBF_EUROPE_WHOLE_NAME = "europe-latest.osm.pbf"

    # the folder path, in which all .csv population density files are stored
    POP_DEN_store_path = DATA_PATH + "pop_den/"

    # the updated and integrated population density file is stored in the main data folder
    POP_DEN_file_name = "pop_dsy_merged.csv"
    POP_DEN_file_path = DATA_PATH

    # BIP file path and sheet name, in the same .xlsx file should also contain 'Einwohner_state' and 'Einwohnen' sheets
    BIP_file_path = DATA_PATH
    BIP_file_name = "BIP und Einkommen.xlsx"
    BIP_file_sheet = "BIPhandel"

    # inflation file path and sheet name
    INFLATION_file_path = DATA_PATH
    INFLATION_file_name = "Inflationsrate.xlsx"
    INFLATION_file_sheet = "inflation"

    # monthly ratio file path and sheet name
    MONTH_file_path = DATA_PATH
    MONTH_file_name = "Monatanteil.xlsx"
    MONTH_file_sheet = "monat_anteil"

    # the retail good's relationship between weight and price
    # Euro/Kg
    RLS_retail = 0.48

    # -------------------------------program generated files------------------------------------------------------------

    # the extracted .osm file, containing only the test area's information
    OSM_PATH = DATA_PATH
    OSM_NAME = "test_area.osm"

    # the original-.xlse file-generated input .xlsx file,
    # containing all to-be-calculated shops (and their coordinates)
    input_xlsx_file_path = DATA_PATH
    input_xlsx_file_name = "input_shops.xlsx"
    input_xlsx_file_sheet = "stores"

    # the test area shops' list, generated from Nominatim's results
    test_area_shop_list_path = DATA_PATH
    test_area_shop_list_name = "test_area_shops.xlsx"
    test_area_shop_list_sheet = "stores"


class Test_Env(Common_Env):
    """
    This part is preset for store the parameters for testing and validating of the whole program. If the whole program
    is moved or copied to a new environment, please copy the assignment statements inside Class "Production_Env" and
    change the records accordingly.
    Then in the main program, the statements at the beginning should also be changed from Production_Env to Test_Env.
    Thus, the whole environment can be switched.
    """

