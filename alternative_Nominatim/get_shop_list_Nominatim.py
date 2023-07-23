import time

import requests
import pandas as pd
import os


def shop_list_to_excel(req, path, filename, sheet):
    """write the request json data from Nominatim server into an .xlsx file.
    :param list req: the json data contains shop list info,
    :param str path: the path, in which the shop .xlsx file should be stored,
    :param str filename: the filename of .xlsx file,
    :param str sheet: the sheet name of the .xlsx file.
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

    excel_file.to_excel(path + filename, sheet_name=sheet, index=False)
    print('Data written to .xlsx file.')
    return 0


def get_shop_list_Nominatim(lon1, lat1, lon2, lat2, server_ip, path, filename, sheet, mode=0):
    """Use Nominatim server to generate the shop list within the given area.
    :param float lon1: Minimum longitude of the test area,
    :param float lat1: minimum latitude of the test area,
    :param float lon2: maximum longitude of the test area,
    :param float lat2: maximum latitude of the test area,
    :param str server_ip: the Nominatim server's ip, if not specified, online Nominatim service will be used,
    :param str path: the path, in which the .xlsx file should be stored,
    :param str filename: the filename of .xlsx file,
    :param str sheet: the sheet name of the .xlsx file,
    :param int mode: the searching mode you want to use: mode=0: No shop keyword needed, use default keyword
    "Supermarket"; mode=1: use your keywords(Keywords need to be stored in this function before), mode=2: use keyword
     "shop".
    """

    def main_cal(url, query, viewbox, limit, mode):
        # This is the main querying program for Nominatim.
        # It raises a request to the server and gets results from it.
        # For code's readability, this part of code is separated from other code blocks and placed in the
        # beginning of the function.

        # for mode 1, all keywords in the array will be used to search for matching objects.
        # mode 1 still has error when a few loops finish, TBD, but in most cases mode 0's work is already fine
        req = []
        if mode == 1:
            for shop_num in range(2, len(query)):
                url_params = url + f"?q={query[shop_num]}&polygon_geojson=1&viewbox={viewbox}&bounded=1&dedupe=0" \
                                   f"&countrycodes" \
                                   f"=de&limit={str(limit)}&polygon_threshold=1&format=jsonv2"
                req += requests.get(url_params).json()

        # for mode 0, only search for the keyword "Supermarket"
        elif mode == 0:
            url_params = url + f"?q={query[0]}&polygon_geojson=1&viewbox={viewbox}&bounded=1&dedupe=0&countrycodes" \
                               f"=de&limit={str(limit)}&polygon_threshold=1&format=jsonv2"
            req = requests.get(url_params).json()

        # for mode 2, only search for the keyword "shop"
        elif mode == 2:
            url_params = url + f"?q={query[1]}&polygon_geojson=1&viewbox={viewbox}&bounded=1&dedupe=0&countrycodes" \
                               f"=de&limit={str(limit)}&polygon_threshold=1&format=jsonv2"
            req = requests.get(url_params).json()
        else:
            print("Mode error. Please check your mode, it should be either 0 or 1 or 2.")
            return 0

        return req, len(req)

    # Para init
    # For security reason, https is used here.
    # However, it could raise problems when the local Nominatim server only supports http connections.
    # In such case, please change the transfer protocol back to http://.
    url = "https://" + server_ip + "/search.php"

    # search query, for retail, query is set to "Supermarket" as default
    query = ["Supermarket", "Shop", "Rewe", "Edeka", "Aldi", "Lidi"]

    # for online service, use smaller limit for querying
    if server_ip == "nominatim.openstreetmap.org":
        limit = 50
    else:
        limit = 2000

    # the bounding box of the test area (area 0, 1 and 2)
    # Noted: the bounding box from the previous program is in the format of (min_lon, min_lat, max_lon, max_lat),
    # while the grammar of Nominatim is (left, top, right, bottom).
    # So here the view-box should make change to meet the new demand.
    viewbox = f"{str(lon1)},{str(lat2)},{str(lon2)},{str(lat1)}"

    # run the querying part first time
    req_temp, result_num = main_cal(url, query, viewbox, limit, mode)

    # If the request is more than the limit, then cut the query area into smaller area (half) and retry.
    if result_num == limit:

        print('Area is too big, trying to spilt it into 4 smaller areas (2 * 2).')
        req = []

        # try to split the area into 4 parts and do the querying for each part separately
        breaker = False  # an exit for breaking inner loop
        for lon_num in range(0, 2):
            for lat_num in range(0, 2):

                if breaker:
                    break  # jump out the outer loop and go to the next loop of 9 areas

                # set the new viewbox
                lon_begin = lon1 + (lon2 - lon1) / 2 * lon_num
                lon_end = lon1 + (lon2 - lon1) / 2 * (lon_num + 1)
                lat_begin = lat1 + (lat2 - lat1) / 2 * lat_num
                lat_end = lat1 + (lat2 - lat1) / 2 * (lat_num + 1)
                viewbox_part = f"{str(lon_begin)},{str(lat_end)},{str(lon_end)},{str(lat_begin)}"

                req_temp, result_num = main_cal(url, query, viewbox_part, limit, mode)
                req += req_temp

                if result_num < limit:
                    if lon_num == 1 and lat_num == 1:  # end the loop
                        shop_list_to_excel(req, path, filename, sheet)  # write the results into .xlsx file
                        return 0
                    else:
                        pass
                else:
                    print(f'A subarea has more than {limit} shops inside. Trying to use smaller areas.')
                    breaker = True
                    break  # jump out the inner loop

                time.sleep(1)
                time.sleep(1)

        print('4 areas are still not enough. Trying to spilt it into 9 smaller areas (3 * 3).')
        req = []

        # try to split the area into 9 parts and do the querying for each part separately
        for lon_num in range(0, 3):
            for lat_num in range(0, 3):
                # set the new viewbox
                lon_begin = lon1 + (lon2 - lon1) / 3 * lon_num
                lon_end = lon1 + (lon2 - lon1) / 3 * (lon_num + 1)
                lat_begin = lat1 + (lat2 - lat1) / 3 * lat_num
                lat_end = lat1 + (lat2 - lat1) / 3 * (lat_num + 1)
                viewbox_part = f"{str(lon_begin)},{str(lat_end)},{str(lon_end)},{str(lat_begin)}"

                req_temp, result_num = main_cal(url, query, viewbox_part, limit, mode)
                req += req_temp

                if result_num < limit:
                    if lon_num == 2 and lat_num == 2:  # end the loop
                        shop_list_to_excel(req, path, filename, sheet)  # write the results into .xlsx file
                        return 0
                    else:
                        pass
                else:
                    print(f'A subarea still has more than {limit} shops inside. Please change your input coordinates.')
                    return 0

                time.sleep(1)
                time.sleep(1)

    elif result_num == 0:
        print('No shops found in the chosen area. Please check your input coordinates or keywords and retry.')
        return 0
    else:
        req = req_temp
        shop_list_to_excel(req, path, filename, sheet)  # write the results into .xlsx file
        return 0

# # test code
# get_shop_list_Nominatim(10.51849, 52.26068, 10.53121, 52.26522)
# pass