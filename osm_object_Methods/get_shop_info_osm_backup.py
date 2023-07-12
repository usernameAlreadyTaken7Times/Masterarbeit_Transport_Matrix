import osmium
import os
import re
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
from math import radians, sin, cos, sqrt, atan2


from IO.excel_input import load_excel



def add_shop_info_to_excel(input_excel, sheet_name, building_area):
    """This function aims to write shop data into existing .xlsx file, like shop building area.
    :param str input_excel: The path of the .xlsx file, in which you want to wirte data,
    :param str sheet_name: the sheet name of the .xlsx file, in which you want to write data,
    :param list building_area: the building area of the shops.
    Please note: the building_area list should have the same length as the data in the original .xlsx file.
     """
    excel = load_excel(input_excel, sheet_name)
    excel_file_temp = pd.DataFrame(columns=["lon", "lat", "address", "area"], index=range(len(excel)))
    for row in range(len(excel)):
        excel_file_temp.at[row, "lon"] = excel.values[row][0]
        excel_file_temp.at[row, "lat"] = excel.values[row][1]
        excel_file_temp.at[row, "address"] = excel.values[row][2]
        excel_file_temp.at[row, "area"] = building_area[row]
    excel_file_temp.to_excel(input_excel, sheet_name=sheet_name, index=False)
    print('Building area data added to .xlsx file.')
    return 0


# use haversine formula to calculate the distance from given coordinates
def haversine(lon1, lat1, lon2, lat2):
    """Calculate and return the length (in kilometer) between two points whose geo-coordinates are already known.
    :param float lon1: The longitude of point 1,
    :param float lat1: the latitude of point 1,
    :param float lon2: the longitude of point 2,
    :param float lat2: the latitude of point 2,
    :return: the length between two points.
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

    return R * c


def get_polygon_area(coords):
    """Return the area of the polygon, using input point coordinates sets.
    :param list coords: The point list containing their cartesian plate coordinates, in the form of
     [(x1, y1), (x2, y2), ...... (xn, yn)],
    :return: the area of the polygon.
    """

    # add the first point coordinates again so that the polygon is closed
    coords.append(coords[0])

    # check if the polygon is a self-intersecting polygons
    if Polygon(coords).is_valid:
        pass
    else:
        print('Polygon is self-intersecting, Please recheck your input.')
        return 0

    # calculate the area
    sum_area = 0
    for n_num in range(0, len(coords) - 1):
        sum_area += (coords[n_num][0] * coords[n_num + 1][1] - coords[n_num][1] * coords[n_num + 1][0])

    return abs(sum_area / 2)


def get_node_location_from_id(id, osm_file):
    """Use this function to get a node's location and check if there is 'shop' in node's tags.
    Update: this function is fully replaced by the next one "get_node_location_from_id_list,"
    because the next one can do the search for every way instead of every node.
    Therefore, the efficiency is raised.
    This function should not be used furthermore.
    :param int id: The reference number of node,
    :param str osm_file: the string of osm file."""
    class Nodehandler(osmium.SimpleHandler):

        def __init__(self, node_id):
            """This class can be used to find the node element with given node_id.
            :param long node_id: The to-be-found node's reference id.
            """
            osmium.SimpleHandler.__init__(self)
            self.node_id = node_id
            self.node_lon = 0
            self.node_lat = 0
            self.node_is_shop = False

        def node(self, n):

            # theologically, all nodes are already contained in this osm file, so no need to consider other situations
            if n.id == self.node_id:
                self.node_lon = n.location.lon
                self.node_lat = n.location.lat

                # check if the node is shop
                if 'shop' in n.tags:
                    self.node_is_shop = True

    NH = Nodehandler(id)
    NH.apply_file(osm_file)
    return NH.node_lon, NH.node_lat, NH.node_is_shop


def get_node_location_from_id_list(id_list, osm_file):

    """Use this function to get the location of nodes and check if any of them have a 'shop' tag.
    :param list id_list: The list consisting of node ids,
    :param str osm_file: the string of osm file.
    """

    class Nodelisthandler(osmium.SimpleHandler):

        def __init__(self, node_id_list):
            """This class can be used to find the node element with given node_id_list.
            :param list node_id_list: The to-be-found node's reference id list.
            """
            osmium.SimpleHandler.__init__(self)
            self.node_id_list = node_id_list
            self.node_lon_list = []
            self.node_lat_list = []
            self.node_is_shop = False
            self.node_shop_id = 0

        def node(self, n):

            # theologically, all nodes are already contained in this osm file, so no need to consider other situations
            for node_num in range(len(self.node_id_list)):
                if n.id == self.node_id_list[node_num]:
                    self.node_lon_list.append(n.location.lon)
                    self.node_lat_list.append(n.location.lat)

                    # check if the node is shop
                    if 'shop' in n.tags:
                        self.node_is_shop = True
                        # store the shop id for further use
                        self.node_shop_id = n.id

    NlH = Nodelisthandler(id_list)
    NlH.apply_file(osm_file)
    return NlH.node_lon_list, NlH.node_lat_list, NlH.node_is_shop, NlH.node_shop_id


def get_node_tags_from_id(id, osm_file):
    """Use this function to get a node's tags from the node's reference number.
    :param int id: The reference number of node,
    :param str osm_file: the string of osm file
    """
    class NodeTaghandler(osmium.SimpleHandler):

        def __init__(self, node_id):
            """This class can be used to find the node tags with given node_id.
            :param long node_id: The to-be-found node's reference id.
            """
            osmium.SimpleHandler.__init__(self)
            self.node_id = node_id
            self.tags = {}

        def node(self, n):

            # theologically, all nodes are already contained in this osm file, so no need to consider other situations
            if n.id == self.node_id:
                if len(n.tags) != 0:
                    self.tags = n.tags
                else:
                    self.tags = None

    NTH = NodeTaghandler(id)
    NTH.apply_file(osm_file)
    return NTH.tags

class ShopAreaHandler(osmium.SimpleHandler):
    def __init__(self, lon, lat, keyword_name, keyword_housenumber, keyword_street, lon_org, lat_org, osm_file,
                 mode=0, tlr=0.003):
        """Use input shop's para to get the details about the shop.
        :param float lon: The longitude of the shop way,
        :param float lat: the latitude of the shop way,
        :param str keyword_name: the search name of the shop,
        :param str keyword_housenumber: the housenumber of the shop,
        :param str keyword_street: the street of the shop,
        :param float lon_org: the original point's longitude of the extracted .osm file(min_lon),
        :param float lat_org: the original point's latitude of the extracted .osm file(min_lat),
        :param str osm_file: the path of this osmium class use, for Node searching,
        :param int mode: the searching mode of this osmium program: if mode=0 (default), it only searches for the ways
        that have a 'shop' tag; if mode=1, search for every way's inside nodes and check if they have a shop tag and
        represent a shop,
        :param float tlr: the coordinate tolerance/error of the shop, default=0.0003, approximately 20m in longitude
        and about 33m in latitude.
        """

        osmium.SimpleHandler.__init__(self)

        # para init
        self.lon = lon
        self.lat = lat
        self.searching_name_street = keyword_street
        self.searching_name_housenumber = keyword_housenumber
        self.searching_name_name = keyword_name
        self.lon_org = lon_org
        self.lat_org = lat_org
        self.tlr = tlr
        self.mode = mode
        self.osm_file = osm_file

        self.shop_area = 0

    @staticmethod
    def check_if_find_shop(area):
        """Check if the shop's area is already found. If it is, jump out of the method.
        :param float area: The area of the way.
        """
        if area != 0:
            # TODO: jump out
            pass
        else:
            pass

    def get_area(self, coords):
        """Cal Coordinates should be in pairs.
        :param list coords: The list of nodes that making of the way, in the form of (n.lon, n.lat).
        """

        # translate the input coordinate sets into the cartesian coordinate system with haversine formula
        coords_plate = []
        for n_num in range(0, len(coords)):

            # convert the coordinates into x and y of a cartesian plate system
            x_n = haversine(coords[n_num][0], self.lat_org, self.lon_org, self.lat_org)
            y_n = haversine(self.lon_org, coords[n_num][1], self.lon_org, self.lat_org)

            coords_plate.append((x_n, y_n))

        # area calculating
        area = get_polygon_area(coords)

        return area

    def way(self, w):

        # check if the area of the way is already available, if it is, jump out
        self.check_if_find_shop(self.shop_area)

        # If the previous searching method is "Nominatim" and now try to find matches in .osm file, there could be
        # conflicts or mismatches on the shop information. So here, a checking program is necessary to avoid any
        # further inconvenience.

        # An osm file is sometimes messy. Some shops are plotted as nodes, some are plotted as ways, so the mode is here
        # to check if you need to search for every way's node as well.

        # the condition of checking, based on the input mode, mode=0 means only check if 'shop' in way's tag
        cond = 'shop' in w.tags

        # mode=1 means deeper search for the way's consisting nodes
        if self.mode == 1:

            # search for every node inside way to determine weather inside node is shop, however, it takes time to
            # look into every way's nodes. so by default, it is abandoned.

            # Update: now in the loop,
            # all nodes inside a way are traversed first,
            # and then their reference number is collected in a list.
            # Then the list is used as input to function "get_node_location_from_id_list"
            # to receive a list containing all node's coordinates and weather any node inside has a 'shop'
            # tag.
            # Therefore, the efficiency could be raised.

            # para init
            way_id_list = []
            n_shop_id = 0
            w_n_lon = []
            w_n_lat = []

            for n_temp in w.nodes:
                way_id_list.append(n_temp.ref)

            w_n_lon, w_n_lat, n_temp_is_shop, n_shop_id = get_node_location_from_id_list(way_id_list, self.osm_file)

            cond = ('shop' in w.tags) or n_temp_is_shop

        # check if the way meets the corresponding criterion
        if cond:

            # When the mode=0, the former 'if' code block was not run,
            # so here a new search inside way's nodes is necessary.
            # When mode=1, all needed information is already available after former calculation,
            # so such steps can be dropped.
            if self.mode == 0:

                # para init
                w_n_lon = []
                w_n_lat = []
                way_id_list = []

                for n_temp in w.nodes:
                    # go back to osm file to find the node with the reference number
                    way_id_list.append(n_temp.ref)

                w_n_lon, w_n_lon, n_temp_is_shop, n_shop_id = get_node_location_from_id_list(way_id_list, self.osm_file)
            else:
                pass

            w_center_lon_sum = sum(w_n_lon)
            w_center_lat_sum = sum(w_n_lat)

            # check if the center of the shop way in the area of that from .xlsx list
            # this match can be reached by geographic-information, which means, the center geo-coordinates or any
            # node of the way are in a designated small area assigned by input coordinates from .xlsx file, or it
            # could also be reached by name and address, which means that the name/brand of the shop and also its
            # address is corresponded to those from .xlsx file.

            # Geo_match_1 calculate the average lon and lat of the shop way, but it could miss some shops that are
            # actually certifiable, so geo_match_2 search for every node inside the way to find if any node matches.
            # Hence, the whole way matches either way.

            # ger_match_1 for the geographical criterion: the average coordinates of the way nodes
            geo_match_1 = (self.lon - self.tlr <= (w_center_lon_sum / len(w.nodes)) <= self.lon + self.tlr and
                         self.lat - self.tlr <= (w_center_lat_sum / len(w.nodes)) <= self.lat + self.tlr)

            # geo_match_2 checks if any of the way's node is near the target point
            geo_match_2 = False

            # check if any node inside is in the allowed area
            for n_temp1 in range(0, len(w_n_lon)):

                # if check the inside nodes, use 1/3 or 1/2 of the tolerance, about 10m
                if self.lon - self.tlr / 2 <= w_n_lon[n_temp1] <= self.lon + self.tlr / 2 and \
                         self.lat - self.tlr / 3 <= w_n_lat[n_temp1] <= self.lat + self.tlr / 3:
                    geo_match_2 = True
                    break

            # for name match, first check if the way itself, which have address, have name/brand that meets the demand;
            # For the way which does not have address, use loops to search for its nodes for address and names;

            # name_match init
            name_match = False

            # ------------------------------check if the input name/street/housenumber is available---------------------
            # consider the situation if the input of osm-searching program get a valid name/street/housenumber, if not,
            # give them an empty string or not valid number(-1 for housenumber)
            housenumber_match_temp = False
            if self.searching_name_housenumber:
                # use regular expression to get the first part of housenumber, which is made only of numbers
                # or there maybe housenumber like '13a,' '27b' which is not fit for int calculation
                searching_housenumber_temp = int(re.findall(r'\d+|\D+', self.searching_name_housenumber)[0])

            else:
                searching_housenumber_temp = -1

            name_match_temp = False
            if self.searching_name_name:
                pass
            else:
                self.searching_name_name = ''

            street_match_temp = False
            # in normal situations, street always exists in a log of address

            # ------------------------------------check input name ends here----------------------------------------


            # ---------------------------------check if the address meets the target point criterion-------------
            if 'addr:street' in w.tags and 'addr:housenumber' in w.tags:

                # use regular expression to get the first part of housenumber, which is made only of numbers
                # or there maybe housenumber like '13a,' '27b' which is not fit for int calculation
                searching_housenumber_way_temp = int(re.findall(r'\d+|\D+', w.tags['addr:housenumber'])[0])

                if 'name' in w.tags:
                    # Here the check condition is loosed: only name match and street match is fine, because sometimes
                    # the Nominatim does not return any housenumber, and also sometimes the housenumber is not the same
                    # as that from an .osm file.
                    if self.searching_name_name.lower() == w.tags['name'].lower() and \
                            self.searching_name_street.lower() == w.tags['addr:street'].lower() and \
                            searching_housenumber_temp - 2 <= searching_housenumber_way_temp <= searching_housenumber_temp + 2:
                        name_match = True
                elif 'brand' in w.tags:
                    if self.searching_name_name.lower() == w.tags['brand'].lower() and \
                            self.searching_name_street.lower() == w.tags['addr:street'].lower() and \
                            searching_housenumber_temp - 2 <= searching_housenumber_way_temp <= searching_housenumber_temp + 2:
                        name_match = True
                else:
                    # Here, the way has street and housenumber and also a mark of 'shop,' yet it does not have
                    # any name or brand representing that it is the same shop in the .xlsx file. But it is stored
                    # anyway

                    # to narrow the error, here use no tolerance for housenumber
                    if self.searching_name_street.lower() == w.tags['addr:street'].lower() and \
                            searching_housenumber_temp == searching_housenumber_way_temp:
                        name_match = True

            # have only street and shop tag
            elif 'addr:street' in w.tags:

                # have name tag
                if 'name' in w.tags:

                    # only check successful when the name, street and approximate position (3x tolerance) match
                    # this position check can avoid the situation that on the same street, but two sides, have the
                    # same brand's shop
                    if self.searching_name_name.lower() == w.tags['name'].lower() and \
                            self.searching_name_street.lower() == w.tags['addr:street'].lower() and \
                            self.lon - 3 * self.tlr <= (w_center_lon_sum / len(w.nodes)) <= self.lon + 3 * self.tlr and \
                            self.lat - 3 * self.tlr <= (w_center_lat_sum / len(w.nodes)) <= self.lat + 3 * self.tlr:
                        name_match = True

                # have brand tag
                if 'brand' in w.tags:

                    # likewise, only check successful when the name, street and approximate position (3x tolerance) match
                    if self.searching_name_name.lower() == w.tags['brand'].lower() and \
                            self.searching_name_street.lower() == w.tags['addr:street'].lower() and \
                            self.lon - 3 * self.tlr <= (w_center_lon_sum / len(w.nodes)) <= self.lon + 3 * self.tlr and \
                            self.lat - 3 * self.tlr <= (w_center_lat_sum / len(w.nodes)) <= self.lat + 3 * self.tlr:
                        name_match = True

                # have only shop tag and street, yet no name/brand or housenumber
                else:

                    # likewise, but this time should use stricter check logic(2x tolerance)
                    if self.searching_name_street.lower() == w.tags['addr:street'].lower() and \
                            self.lon - 2 * self.tlr <= (w_center_lon_sum / len(w.nodes)) <= self.lon + 2 * self.tlr and \
                            self.lat - 2 * self.tlr <= (w_center_lat_sum / len(w.nodes)) <= self.lat + 2 * self.tlr:
                        name_match = True

            # all other possibilities: have housenumber but no street; or have neither housenumber nor street, so in
            # order to find information to match, we have to dig deeper into the way's consisting nodes
            else:
                node_num = 0
                # check for the lower nodes for further information
                for n_temp2 in w.nodes:

                    # get the way node's tags
                    n_temp2_tags = {}
                    n_temp2_tags = get_node_tags_from_id(n_temp2.ref, self.osm_file)

                    if n_temp2_tags is not None:
                        if 'addr:street' in n_temp2_tags and 'addr:housenumber' in n_temp2_tags:

                            # likewise, use regular expression to get the first part of housenumber, which is made only of
                            # numbers or there maybe housenumber like '13a', '27b' which is not fit for int calculation
                            searching_housenumber_node_temp = int(
                                re.findall(r'\d+|\D+', n_temp2_tags['addr:housenumber'])[0])

                            # the node has a name tag
                            if 'name' in n_temp2_tags:
                                if self.searching_name_name.lower() == n_temp2_tags['name'].lower() and \
                                        self.searching_name_street.lower() == n_temp2_tags['addr:street'].lower() and \
                                        searching_housenumber_temp - 1 <= searching_housenumber_node_temp <= searching_housenumber_temp + 1:
                                    name_match = True

                            # the node has a brand tag
                            elif 'brand' in n_temp2_tags:
                                if self.searching_name_name.lower() == n_temp2_tags['brand'].lower() and \
                                        self.searching_name_street.lower() == n_temp2_tags['addr:street'].lower() and \
                                        searching_housenumber_temp - 1 <= searching_housenumber_node_temp <= searching_housenumber_temp + 1:
                                    name_match = True

                            else:
                                # the node's street match and housenumber match
                                if self.searching_name_street.lower() == n_temp2_tags['addr:street'].lower() and \
                                        searching_housenumber_temp == searching_housenumber_node_temp:
                                    name_match = True

                        # this time node has only the street but no housenumber
                        elif 'addr:street' in n_temp2_tags:
                            if 'name' in n_temp2_tags:
                                if self.searching_name_name.lower() == n_temp2_tags['name'].lower() and \
                                        self.searching_name_street.lower() == n_temp2_tags['addr:street'].lower() and \
                                        self.lon - self.tlr <= w_n_lon[node_num] <= self.lon + self.tlr and \
                                        self.lat - self.tlr <= w_n_lat[node_num] <= self.lat + self.tlr:
                                    name_match = True
                            elif 'brand' in n_temp2.tags:
                                if self.searching_name_name.lower() == n_temp2_tags['brand'].lower() and \
                                        self.searching_name_street.lower() == n_temp2_tags['addr:street'].lower() and \
                                        self.lon - self.tlr <= w_n_lon[node_num] <= self.lon + self.tlr and \
                                        self.lat - self.tlr <= w_n_lat[node_num] <= self.lat + self.tlr:
                                    name_match = True

                            # only have a street, no number or any available names
                            else:
                                if self.searching_name_street.lower() == n_temp2_tags['addr:street'].lower() and \
                                        self.lon - 2 * self.tlr <= w_n_lon[node_num] <= self.lon + 2 * self.tlr and \
                                        self.lat - 2 * self.tlr <= w_n_lat[node_num] <= self.lat + 2 * self.tlr:
                                    name_match = True

                        # this node has no usable information, go back to loop and check the next one
                        else:
                            pass
                    else: # the node's tag is empty
                        # node contains no information
                        pass
                    node_num += 1

            # --------------------------------------name_match check ends here---------------------------------------

            # searching process ends here and now use "name_match," "geo_match1" and "geo_match2" to determine weather
            # way is the one in .xlsx file
            if name_match or geo_match_1 or geo_match_2:
                print('Find match in .xlsx file.')

                # get every node's coordinates that are part of this shop way
                coords = []
                for n_num in range(len(w.nodes)):
                    coords.append((w_n_lon[n_num], w_n_lat[n_num]))
                self.shop_area = self.get_area(coords)
            else:
                print('Shop match fails.')
        else:
            print('Way is not shop.')


def get_shop_info_osm(lon_org, lat_org, bbox=0.0003,
                      osm_file="C:/Users/86781/PycharmProjects/pythonProject/data/test_area.osm",
                      xlsx_file1="C:/Users/86781/PycharmProjects/pythonProject/data/shop_list_coordinates.xlsx",
                      xlsx_file2="C:/Users/86781/PycharmProjects/pythonProject/data/test_area_shops.xlsx",
                      xlsx_file_sheet1="stores", xlsx_file_sheet2="stores",
                      previous_searching_method="Nominatim"):
    """This function is used to get the shop information from .osm.pbf file, in order to calculate their attractions
     in the following steps. The longitude and latitude should be able to be found in the .xlsx file, which was
     generated before by a script using Nominatim service or an .osm.pbf traversal program.
     :param float lon_org: The origin point's longitude of the .osm file, manually set as the left-bottem point,
     :param float lat_org: the origin point's latitude of the .osm file, manually set as the left-bottem point,
     :param float bbox: The offset or tolerance of the coordinates, default as 0.0003. In the german region it is
      about 20m in longitude and about 33m in latitude,
     :param str osm_file: the .osm.pbf file, in which the shops' information is stored,
     :param str xlsx_file1: the .xlsx file, generated from former script, containing geo-coordinates of the shops in
      area 0, (only the ones whose cargo volume is going to be calculated)
     :param str xlsx_file2: the .xlsx file, generated from former script, containing geo-coordinates of the shops in
      area 0,1 and 2,
     :param str xlsx_file_sheet1: the workbook name of xlsx_file1,
     :param str xlsx_file_sheet2: the workbook name of xlsx_file2,
     :param str previous_searching_method: the searching method of the previous steps: can choose from "osm" or
      "Nominatim", default as "Nominatim".
     :return: TBD,
     :rtype: TBD
    """

    if previous_searching_method == "Nominatim" or previous_searching_method == "osm":
        pass
    else:
        print('Please specify the previous searching method from "Nominatim" or "osm".')

    # check if the file exists
    if os.path.exists(xlsx_file1) and os.path.exists(xlsx_file2) and os.path.exists(osm_file):
        pass
    else:
        print('Please check your input .xlsx & .osm files.')
        return 0

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
            if excel_file2.values[j][0] - bbox <= excel_file1.values[i][0] <= excel_file2.values[j][0] + bbox \
                    and excel_file2.values[j][1] - bbox <= excel_file1.values[i][1] <= excel_file2.values[j][1] + bbox:
                area_0_num.append(j)
                break

            # if it is already the end of excel_2, and still no match is found, then write -1 to area_0_num and write
            # the index of excel_1 to area_0_idc
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
              f'Please search for it/them manually.')
        # TODO: find shops
        pass
    elif len(area_0_num) < len(excel_file1):
        print('All shops\' coordinates found.')
    else:
        # Normally this should not happen, or?
        pass

    # --------------------------------extinguish process finish--------------------------------------------------------

    # from shop_address to separate the shop name, shop housenumber and shop street using regular expression
    # P.S. regular expression really makes me bald:-( I don't want to see it ever again if it is possible.
    # thanks to Stack Overflow community and no less than 30 web pages, I literally got nothing and choose to use
    # if-else condition check back

    # Update: I finally choose to abandon regular regression because it does not have a good match to the string.
    # Now I choose the complex but reliable if-else loops.

    '''
    # This function can also run, but it does not have good strengh of spilting german address.
    def extract_shop_details(shop_address):
        """This function can be used to separate the name, housenumber and street (if available) of the shop
        and return them individually.
        :param str shop_address: The address string of the shop, all information contained and divided by comma."""
        shop_name = re.findall(r"^[^,]+", shop_address)
        shop_house_number = re.findall(r"\b\d+\b", shop_address)
        shop_street = re.findall(r"(?<=\d\s)[^,]+", shop_address)

        return shop_name[0].strip() if shop_name else '', \
            shop_house_number[0] if shop_house_number else '', \
            shop_street[0].strip() if shop_street else ''
    '''

    def extract_shop_details(address):
        """This function is used to separate the name, housenumber and street of a shop from its address string.
         Please note: sometimes in the Nominatim server's result, the name or the housenumber is not available. But it is
          assumed that they will not be absent at the same time.
          :param str address: The string of the shop address, containing housenumber, shop name and street at the same time.
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
            # some housenumber have one character at the end, like '15a', ''30c'
            if slt[num_temp1].isdigit() or slt[num_temp1][0:-1].isdigit():
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


    shop_areas = []



    for shop_num in range(0, len(excel_file2)):

        print(f'Working on the {shop_num+1}. shop, {len(excel_file2)} shops in total.')

        # separate the strings
        shop_name, shop_housenumber, shop_street = extract_shop_details(shop_address[shop_num])

        # use osmium.SimpleHandler to find information of the shops
        SAH = ShopAreaHandler(excel_file2.values[shop_num][0], excel_file2.values[shop_num][1],
                              shop_name, shop_housenumber, shop_street,
                              lon_org, lat_org, osm_file)
        SAH.apply_file(osm_file)
        shop_area_temp = SAH.shop_area

        # store the area of the shop
        shop_areas.append(shop_area_temp)

    # store the list with building area data back to the original .xlsx file
    add_shop_info_to_excel(xlsx_file1, xlsx_file_sheet1, shop_areas)
    print('All shops\' building area stored into the original .xlsx file.')
    return 0


# test code

# get_shop_info_osm(0.0003)
# SAH1 = ShopAreaHandler('abc', '63', 'Rebenring', 'braunschweig')
# SAH1.apply_file("D:/test/braun-part.osm")
# print(SAH.total_area)

# b = haversine(10.0000, 52.0000, 10.0003, 52.0000)
# a = get_polygon_area([(0,1), (1,1), (1,0), (0,0), (-3,-3)])
get_shop_info_osm(10.46843, 52.25082)
pass
