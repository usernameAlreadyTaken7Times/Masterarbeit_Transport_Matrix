import requests
import pandas as pd
import os
from math import radians, sin, cos, sqrt, atan2


def haversine(lon1, lat1, lon2, lat2):
    """This function uses haversine formula to calculate the distance from given coordinates
    and return the length (in meters) between two points whose geo-coordinates are already known.
    :param float lon1: The longitude of point 1,
    :param float lat1: the latitude of point 1,
    :param float lon2: the longitude of point 2,
    :param float lat2: the latitude of point 2,
    :rtype float
    :return: the length between two points in kilometer.
    """

    # approximate radius of earth in km
    R = 6373.0

    # Convert coordinate angles to radians
    lon1_r = radians(lon1)
    lat1_r = radians(lat1)
    lon2_r = radians(lon2)
    lat2_r = radians(lat2)

    # calculate the coordinates' difference
    diff_lon = lon2_r - lon1_r
    diff_lat = lat2_r - lat1_r

    a = sin(diff_lat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(diff_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c * 1000


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


def get_shop_list_Nominatim(lon1, lat1, lon2, lat2, server_ip, path, filename, sheet, mode=1):
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

    # Para init
    # For security reason, https is used here.
    # However, it could raise problems when the local Nominatim server only supports http connections.
    # In such case, please change the transfer protocol back to http://.
    url = "https://" + server_ip + "/search.php"

    # search query, for retail, query is set to "Supermarket" as default
    query = ["Supermarket", "Shop", "Rewe", "Edeka", "Aldi", "Lidi", "Rossmann","ikea", "Tchibo", "dm", "Karstadt",
             "Douglas", "Kaufland", "OBI", "C&A", "Fielmann", "Deichmann", "Weltbild", "Otto", "H&M", "Saturn", "Real",
             "Kaufhof", "Hornbach", "Netto", "Fressnapf", "Esprit", "Neckermann", "Thalia", "Bauhaus", "Media Markt",
             "S. Oliver", "Zalando", "Penny", "Müller", "Apollo Optik", "NewYorker", "Praktiker", "Intersport",
             "Karstadt Sports"]

    # for online service, use smaller limit for querying
    if server_ip == "nominatim.openstreetmap.org":  # here I just assume all other ip means a offline server
        limit = 50
    else:
        limit = 999999  # for offline servers, there is no limitation

    def main_cal(url, query, viewbox, limit, mode):
        """This is the main querying program for Nominatim.
         It raises a request to the server and gets results from it.
         For code's readability, this part of code is separated from other code blocks and placed at the
         beginning of the function.

         Please note: this function is not fit for mode 1.
         """
        req = []

        if mode == 0:
            url_params = url + f"?q={query[0]}&polygon_geojson=1&viewbox={viewbox}&bounded=1&dedupe=0&countrycodes" \
                               f"=de&limit={str(limit)}&polygon_threshold=1&format=jsonv2"
            req = requests.get(url_params).json()

        # for mode 2, only search for the keyword "shop"
        elif mode == 2:
            url_params = url + f"?q={query[1]}&polygon_geojson=1&viewbox={viewbox}&bounded=1&dedupe=0&countrycodes" \
                               f"=de&limit={str(limit)}&polygon_threshold=1&format=jsonv2"
            req = requests.get(url_params).json()
        else:
            print("Mode error. Please check your mode, it should be either 0 or 2.")
            return 0

        return req, len(req)

    def main_cal_mode1(url, query, viewbox, limit):
        """Like the one function before, this function only works for mode1, which involves more than one keyword.
        """

        # for mode 1, all keywords in the array will be used to search for matching objects.
        # mode 1 still has error when a few loops finish, TBD, but in most cases mode 0's work is already fine
        req = []

        url_params = url + f"?q={query}&polygon_geojson=1&viewbox={viewbox}&bounded=1&dedupe=0" \
                           f"&countrycodes" \
                           f"=de&limit={str(limit)}&polygon_threshold=1&format=jsonv2"
        req += requests.get(url_params).json()

        return req, len(req)

    # the bounding box of the test area (area 0, 1 and 2)
    # noted: the bounding box from the previous program is in the format of (min_lon, min_lat, max_lon, max_lat),
    # while the grammar of Nominatim is (left, top, right, bottom)
    # so here the view-box should make change to meet the new demand.
    viewbox = f"{str(lon1)},{str(lat2)},{str(lon2)},{str(lat1)}"

    # with one simple keyword (mode 0 or mode 2), use such method as below
    if mode == 0 or mode == 2:
        # run the querying part first time
        req_temp, result_num = main_cal(url, query, viewbox, limit, mode)

        # If the request is more than the limit, then cut the query area into smaller area (half) and retry.
        if result_num == limit:

            print('Area is too big, trying to spilt it into 4 smaller areas (2 * 2).')
            req = []

            # try to split the area into four parts and do the querying for each part separately
            breaker = False  # an exit for breaking inner loop
            for lon_num in range(0, 2):
                if breaker:
                    break  # jump out the outer loop and go to the next loop of 36 areas

                for lat_num in range(0, 2):

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

                    # if the server does not support continually searching, sleep for 1 sec
                    # time.sleep(1)

            print('4 areas are still not enough. Trying to spilt it into 36 smaller areas (6 * 6).')
            req = []

            # try to split the area into 36 parts and do the querying for each part separately
            for lon_num in range(0, 6):
                for lat_num in range(0, 6):
                    # set the new viewbox
                    lon_begin = lon1 + (lon2 - lon1) / 6 * lon_num
                    lon_end = lon1 + (lon2 - lon1) / 6 * (lon_num + 1)
                    lat_begin = lat1 + (lat2 - lat1) / 6 * lat_num
                    lat_end = lat1 + (lat2 - lat1) / 6 * (lat_num + 1)
                    viewbox_part = f"{str(lon_begin)},{str(lat_end)},{str(lon_end)},{str(lat_begin)}"

                    req_temp, result_num = main_cal(url, query, viewbox_part, limit, mode)
                    req += req_temp

                    if result_num < limit:
                        if lon_num == 5 and lat_num == 5:  # end the loop
                            shop_list_to_excel(req, path, filename, sheet)  # write the results into .xlsx file
                            return 0
                        else:
                            pass
                    else:
                        print(f'A subarea still has more than {limit} shops inside. '
                              f'Please change your input coordinates.')
                        return 0

                    # if the server does not support continually searching, sleep for 1 sec
                    # time.sleep(1)

        elif result_num == 0:
            print('No shops found in the chosen area. Please check your input coordinates or keywords and retry.')
            return 0
        else:
            req = req_temp
            shop_list_to_excel(req, path, filename, sheet)  # write the results into .xlsx file
            return 0

    # mode=1 situation, more than one keyword is used to get a detailed retail shop list
    elif mode == 1:

        # set a list to store all request results altogether
        req_whole = []

        # set a para to determine how many subareas should be cut.
        # the bigger the area is, the more subareas there are.
        sub_area_side_num = max(round((lon2 - lon1) / 0.02), round((lat2 - lat1) / 0.01)) + 1

        # use loop to search for every keyword inside list "query"
        for query_num in range(len(query)):
            req = []
            # first run the request for one time, if the result is too much, then cut the area into subareas
            req_temp, result_num = main_cal_mode1(url, query[query_num], viewbox, limit)

            if result_num == limit:

                print("***********************************************************************************************")
                print(f'Result is too many for keyword {str(query[query_num])},'
                      f' trying to spilt the area into {str(sub_area_side_num * sub_area_side_num)} small areas'
                      f' ({str(sub_area_side_num)} * {str(sub_area_side_num)}).')
                req_part = []

                # loop in every subarea to find shops
                for lon_num in range(0, sub_area_side_num):
                    for lat_num in range(0, sub_area_side_num):

                        print("---------------------------------------------------------------------------------------")
                        print(f"searching for keyword {str(query[query_num])} "
                              f"in {str(lon_num * sub_area_side_num + lat_num)}. small areas,"
                              f" {str(sub_area_side_num * sub_area_side_num)} small areas in total.")

                        # set the new viewbox
                        lon_begin = lon1 + (lon2 - lon1) / sub_area_side_num * lon_num
                        lon_end = lon1 + (lon2 - lon1) / sub_area_side_num * (lon_num + 1)
                        lat_begin = lat1 + (lat2 - lat1) / sub_area_side_num * lat_num
                        lat_end = lat1 + (lat2 - lat1) / sub_area_side_num * (lat_num + 1)
                        viewbox_part = f"{str(lon_begin)},{str(lat_end)},{str(lon_end)},{str(lat_begin)}"

                        # retrieve result
                        req_temp, result_num = main_cal_mode1(url, query[query_num], viewbox_part, limit)

                        if result_num < limit:
                            req_part += req_temp
                            if lon_num == (sub_area_side_num - 1) and lat_num == (sub_area_side_num - 1):  # end the loop
                                print(
                                    f'Found {str(len(req_part))} shops with keyword "{str(query[query_num])}" in the chosen area.')
                                req += req_part

                        else:
                            print(f'A subarea has more than {limit} shops inside.'
                                  f' Trying to split this area into four subareas.')
                            # try to cut this area into four sub subareas and retry
                            for subarea_lon_num in range(0, 2):
                                for subarea_lat_num in range(0, 2):
                                    subarea_lon_begin = lon_begin + (lon_end - lon_begin) / 2 * subarea_lon_num
                                    subarea_lon_end = lon_begin + (lon_end - lon_begin) / 2 * (subarea_lon_num + 1)
                                    subarea_lat_begin = lat_begin + (lat_end - lat_begin) / 2 * subarea_lat_num
                                    subarea_lat_end = lat_begin + (lat_end - lat_begin) / 2 * (subarea_lat_num + 1)
                                    viewbox_subarea = f"{str(subarea_lon_begin)},{str(subarea_lat_end)},{str(subarea_lon_end)},{str(subarea_lat_begin)}"

                                    req_temp_sub, result_num_sub = main_cal_mode1(url, query[query_num], viewbox_subarea, limit)

                                    # here we assume there is no beyond limitation result, write the result back to para
                                    req_part += req_temp_sub

                            if lon_num == (sub_area_side_num - 1) and lat_num == (sub_area_side_num - 1):  # end the loop
                                print(
                                    f'Found {str(len(req_part))} shops with keyword "{str(query[query_num])}" in the chosen area.')
                                req += req_part

                        # if the server does not support continually searching, sleep for 1 sec
                        # time.sleep(1)

            elif result_num == 0:
                print(f'No shops found with keyword "{str(query[query_num])}" in the chosen area.')
            else:
                print(f'Found {str(len(req_temp))} shops with keyword "{str(query[query_num])}" in the chosen area.')
                req += req_temp

            req_whole += req

        # use place id to find and delete duplicates
        place_id_list = []
        unique_req_temp = []

        # here, try to find a solid method to distinguish weather any shop exists more than one time.
        # however, user-generated data can be messy:
        # some shops appear more than once but with different IDs and same coordinates.

        # so here, the shops with the same id will be deleted
        for req_record in req_whole:
            if "place_id" in req_record.keys():
                if req_record["place_id"] not in place_id_list:
                    place_id_list.append(req_record["place_id"])
                    unique_req_temp.append(req_record)

        address_temp = []
        coordinates_temp = []
        unique_req = []

        # check if there's any shop with the same address, different place_id but really close to other shops
        for req_record_temp in unique_req_temp:
            if req_record_temp["display_name"] not in address_temp:
                address_temp.append(req_record_temp["display_name"])
                coordinates_temp.append((req_record_temp["lon"], req_record_temp["lat"]))
                unique_req.append(req_record_temp)
            else:
                # the address was already in the store list,
                # now we should check if the straight line distances between this shop and other shops are less then
                # the limitation

                # search for the index of the same address
                order_index = address_temp.index(req_record_temp["display_name"])

                distance_shops = haversine(float(coordinates_temp[order_index][0]),
                                           float(coordinates_temp[order_index][1]),
                                           float(req_record_temp["lon"]),
                                           float(req_record_temp["lat"]))
                if distance_shops <= 20:
                    # when the distance is smaller than 20m, then they are assumed as the same shop
                    # and in that case, no new record is written
                    pass
                else:
                    address_temp.append(req_record_temp["display_name"])
                    coordinates_temp.append((req_record_temp["lon"], req_record_temp["lat"]))
                    unique_req.append(req_record_temp)

        # check if there's any shop with the same name, different place_id, but the distance is less than 10m

        # write the results into .xlsx file
        shop_list_to_excel(unique_req, path, filename, sheet)
        print("-------------------------------------------------------------------------------------------------------")

    else:
        print("Mode error.")
        return 0

# # test code
# get_shop_list_Nominatim(10.5858, 51.7162, 10.6367, 51.7346, "nominatim.openstreetmap.org",
#                             "C:/Users/86781/PycharmProjects/pythonProject/data/",
#                         "test_area_shops.xlsx", "stores", 1)
#
# get_shop_list_Nominatim(9.76195, 52.39727, 9.77468, 52.40180, "nominatim.openstreetmap.org",
#                             "C:/Users/86781/PycharmProjects/pythonProject/data/",
#                         "input_shops.xlsx", "stores", 1)
#
# pass
