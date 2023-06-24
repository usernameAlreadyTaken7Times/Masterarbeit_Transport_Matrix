import requests
import pandas as pd
import os


def shop_list_to_excel(req, path='C:/Users/86781/PycharmProjects/pythonProject/data/', filename='test_area_shops.xlsx'):
    """write the request json data from Nominatim server into an .xlsx file.
    :param list req: the json data contains shop list info,
    :param str path: the path, in which the store .xlsx file should be stored,
    :param str filename: the filename of .xlsx file.
    """
    # delete the file that already exists
    if os.path.exists(path + filename):
        os.remove(path + filename)

    excel_file = pd.DataFrame(
        columns=["lon", "lat", "address"], index=range(len(req)))

    # write json data into the .xlsx file
    for row in range(len(req)):
        excel_file.at[row, "lon"] = float(req[row]["lon"])
        excel_file.at[row, "lat"] = float(req[row]["lat"])
        excel_file.at[row, "address"] = req[row]["display_name"]

    excel_file.to_excel(path + filename, sheet_name="stores", index=False)
    print('Data written to .xlsx file.')
    return 0


def get_shop_list_Nominatim(lon1, lat1, lon2, lat2, server_ip="nominatim.openstreetmap.org", mode=0):
    """Use Nominatim server to generate the shop list within the given area.
    :param float lon1: Minimum longitude of the test area,
    :param float lat1: minimum latitude of the test area,
    :param float lon2: maximum longitude of the test area,
    :param float lat2: maximum latitude of the test area,
    :param str server_ip: the Nominatim server's ip, if not specified, online Nominatim service will be used,
    :param int mode: the searching mode you want to use: mode=0: No shop keyword needed, use default keyword
    "Supermarket"; mode=1: use your keywords(Keywords need to be stored in this function before), mode=2: use keyword
     "shop".
    """

    # For security reason, https is used here.
    # However, it could raise problems when the local Nominatim server only supports http connections.
    url = "https://" + server_ip + "/search.php"

    # The bounding box of the test area(area 0, 1 and 2)
    # Noted: the bounding box from the previous program is in the format of (min_lon, min_lat, max_lon, max_lat),
    # while the grammar of Nominatim is (left, top, right, bottom). So here the view-box should make change to meet the
    # new demand.
    viewbox = f"{str(lon1)},{str(lat2)},{str(lon2)},{str(lat1)}"

    # search query, for retail, query is set to "Supermarket" as default
    # TODO: find more shop names to meet the demand of "retail"
    query = ["Supermarket", "Shop", "Rewe", "Edeka", "Aldi", "Lidi"]

    # for online service, use smaller limit for querying
    if server_ip == "nominatim.openstreetmap.org":
        limit = 50
    else:
        limit = 100

    # for mode 1, all keywords in the array will be used to search for matching objects.
    # TODO: mode 1 still has error when a few loops finish, TBD, but in most cases mode 0's work is already fine
    if mode == 1:
        req = []
        for shop_num in range(2, len(query)):
            url_params = url + f"?q={query[shop_num]}&polygon_geojson=1&viewbox={viewbox}&bounded=1&dedupe=0" \
                               f"&countrycodes" \
                                f"=de&limit={str(limit)}&polygon_threshold=1&format=jsonv2"
            req += requests.get(url_params).json()

    # for mode 0, only search for the keyword "Supermarket"
    elif mode == 0:
        req = []
        url_params = url + f"?q={query[0]}&polygon_geojson=1&viewbox={viewbox}&bounded=1&dedupe=0&countrycodes" \
                           f"=de&limit={str(limit)}&polygon_threshold=1&format=jsonv2"
        req = requests.get(url_params).json()

    # for mode 2, only search for the keyword "shop"
    elif mode == 2:
        req = []
        url_params = url + f"?q={query[1]}&polygon_geojson=1&viewbox={viewbox}&bounded=1&dedupe=0&countrycodes" \
                           f"=de&limit={str(limit)}&polygon_threshold=1&format=jsonv2"
        req = requests.get(url_params).json()
    else:
        print("Mode error. Please check your mode, it should be either 0 or 1 or 2.")
        return 0

    # TODO: if return more than limit(50/100) how to do?
    # cut the query area into smaller area and retry



    if req:
        shop_list_to_excel(req)
        return 0
    else:
        print('No shops found in the chosen area. Please check your input coordinates and retry.')
        return 0

# # test code
# get_shop_list_Nominatim(13.0621, 52.3777, 13.8764, 52.6664)
# pass