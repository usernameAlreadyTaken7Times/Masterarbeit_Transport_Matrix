import os
import pandas as pd
import numpy as np
import requests


def shop_list_to_excel(req, path='C:/Users/86781/PycharmProjects/pythonProject/data/',
                       filename='shop_list_coordinates.xlsx'):
    """write the request json data containing geo info from Nominatim server into an .xlsx file.
        :param list req: the json data contains shop coordinate info,
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


def get_coordinate_from_address_Nominatim(shop_list, server_ip="nominatim.openstreetmap.org", limitation=50):
    """This function can be used to transform the input shop names and addresses to their geo coordinates.
    :param list shop_list: The to-be-searched shop list, containing all names and addresses of the shops, and
    should be in the form of shop_list=[name, housenumber, street, city, state]. For this project, only
    valid addresses in Germany will be searched,
    :param str server_ip: the Nominatim server's ip, if not specified, online Nominatim service will be used,
    :param int limitation: the Nominatim server's query limitation, only used for online service, default=50.
    :return: A modified shop list, in the form of new_shop_list=[lon, lat, address].
    """

    # For security reason, https is used here.
    # However, it could raise problems when the local Nominatim server only supports http connections.
    url = "https://" + server_ip + "/search.php"

    # for online service, use smaller limit for querying
    if server_ip == "nominatim.openstreetmap.org":
        limit = limitation
    else:
        # for local Nominatim service, the query limitation is set to 2000, and that should be enough for almost all
        # situations
        limit = 2000

    # extract shop data from shop_list
    name = []
    housenumber = []
    street = []
    city = []
    state = []

    # check if the shop list contains only one record
    # more than one records in a two-dimensional array -> normal
    if len(np.array(shop_list).shape) == 2:
        for shop_num_temp1 in range(0, len(shop_list)):
            name.append(str(shop_list[shop_num_temp1][0]))
            housenumber.append(str(shop_list[shop_num_temp1][1]))
            street.append(str(shop_list[shop_num_temp1][2]))
            city.append(str(shop_list[shop_num_temp1][3]))
            state.append(str(shop_list[shop_num_temp1][4]))

    # shop list has only one record
    elif len(np.array(shop_list).shape) == 1:
        name.append(str(shop_list[0]))
        housenumber.append(str(shop_list[1]))
        street.append(str(shop_list[2]))
        city.append(str(shop_list[3]))
        state.append(str(shop_list[4]))

    # a three-dimensional array? Come on, there must be something really, really bad happens:-)
    else:
        print('Please check your input shop list. The format is not valid.')
        return 0

    # store request results
    req = []

    # search for every record in the shop_list
    for shop_num_temp2 in range(0, len(name)):

        url_params = url + f'?q={housenumber[shop_num_temp2]}+{street[shop_num_temp2]}+{city[shop_num_temp2]}&' \
                            f'polygon_geojson=1&bounded=1&dedupe=0&countrycodes' \
                           f'=de&limit={str(limit)}&polygon_threshold=1&format=jsonv2'
        jsn = requests.get(url_params).json()

        # check if the result is valid
        if len(jsn) == 0:
            print('No result returned. Using other keyword instead.')

            # if housenumber-street-city keyword does not get a valid result, retry name-street-city keyword instead
            url_params = url + f'?q={name[shop_num_temp2]}+{street[shop_num_temp2]}+{city[shop_num_temp2]}&' \
                               f'polygon_geojson=1&bounded=1&dedupe=0&countrycodes' \
                               f'=de&limit={str(limit)}&polygon_threshold=1&format=jsonv2'
            jsn_temp = requests.get(url_params).json()

            # check if the new keyword found any match coordinate pairs
            if len(jsn_temp) == 0:
                print(f'The {shop_num_temp2 + 1}. shop\'s coordinates cannot be found. Please retry with other ways '
                      f'instead.')
            elif len(jsn_temp) == 1:
                req.append(jsn_temp)
            else:
                print(
                    f'The {shop_num_temp2 + 1}. shop\'s new keyword match more than one coordinate pair. Here, only '
                    f'the first pair is used and stored.')
                req.append(jsn_temp[0])

        # ideal situation: one address match one pair of coordinates
        elif len(jsn) == 1:
            req.append(jsn[0])

        # if match more than one pair of coordinates
        else:

            # check if the name of the shop can be found in the returned json arrays, if it can be, use its coordinates
            name_match = False
            for shop_num_temp3 in range(0, len(jsn)):
                if 'display_name' in jsn[shop_num_temp3].keys() and name[shop_num_temp2].lower().split() in jsn[shop_num_temp3]['display_name'].lower().split():
                    req.append(jsn[shop_num_temp3])
                    print(
                        f'The {shop_num_temp2 + 1}. shop\'s address match more than one coordinate pair. Here the pair'
                        f'that match the name will be used and stored.')
                    name_match = True
                    break
            if name_match:
                pass
            else:
                print(
                    f'The {shop_num_temp2 + 1}. shop\'s address match more than one coordinate pair. Here, the first '
                    f'pair is used and stored.')
                req.append(jsn[0])

    shop_list_to_excel(req)
    return 0
