from xml.dom.minidom import parse
import xml.dom.minidom

from shapely.geometry import Point
# from shapely.geometry.polygon import Polygon

from math import radians, sin, cos, sqrt, atan2
from shapely.geometry import Polygon
from osm_time.opening_hours import OpeningHours
import numpy as np


def get_shop_way_ref_osm(lon_list, lat_list, name_list, housenumber_list, street_list, osm_file, tlr, lon_org, lat_org,
                         check_node=1, predict_node_boundary=0, keyword_as_supermarket=0):
    """
     As a supplement to the osm search program,
     this program uses Python to directly process the osm file in xml format
     and return the building areas for a list of the chosen store way(if available),
     as well as their infrastructure grades.

     :param list lon_list: The longitude list of the shop ways,
     :param list lat_list: the latitude list of the shop ways,
     :param list name_list: the search name list of the shops,
     :param list housenumber_list: the housenumber list of the shops,
     :param list street_list: the street lists of the shops,
     :param str osm_file: the path of the osmium file of the test area in use, for way searching,
     :param float tlr: the coordinate tolerance/error of the shop, default=0.0003, approximately 20m in longitude
      and about 33m in latitude,
     :param float lon_org: the origin point's longitude of the .osm file, manually set as the left-bottem point,
     :param float lat_org: the origin point's latitude of the .osm file, manually set as the left-bottem point,
     :param int check_node: the searching mode of this osmium program: if check_node=0 (default), it only searches for
      the ways that have a 'shop' tag; if check_node=1, search for every way's inside nodes and check if they have a
      shop tag and represent a shop,
     :param int predict_node_boundary: if the shop is found as a node and not part of a way, then the area can not be
      calculated. Then if predict_node_boundary=1, then the program will loop to find the smallest way containing the
      shop node and use the way's area as shop area. If predict_node_boundary=0, the program will use a standard shop
      area, 80m^2. Default predict_node_boundary=0,
     :param int keyword_as_supermarket: the searching keyword condition, weather use a "Supermarket" or just "shop".
     In an .osm file, the range of an element with a "shop" tag is rather wide: it does not have to be a retail shop.
     So if you want to make it strict, then you can set keyword_as_supermarket=1, and it means force use "Supermarket"
     as searching keyword instead of "shop."
     Doing so may improve the search efficiency, but it may also increase the probability of matching failures.
     Specifically, the returned tag information and building area are empty.
     """

    # -------------------------------inner function zone-----------------------------------------

    def get_way_nodes_coordinates_with_ref(node_list, nodes):
        """Use the input list containing way's nodes and return their coordinates.
            :param list node_list: A list containing the way's node reference numbers,
            :param nodes: the document node elements from osm xml file,
            :return: the center coordinates (longitude, latitude) of the way.
            """

        way_coor_list = []

        for node_list_num in range(len(node_list)):  # for every node in the node list
            for node in nodes:
                if str(node_list[node_list_num]) == node.getAttribute("id"):
                    # store all nodes of the way into the array
                    way_coor_list.append((float(node.getAttribute("lon")), float(node.getAttribute("lat"))))
                    break

        return way_coor_list

    def cal_way_center(node_list, nodes):
        """Use the input list containing way's nodes to calculate the way's center coordinates.
            :param list node_list: A list containing the way's node reference numbers,
            :param nodes: the document node elements from osm xml file,
            :return: the center coordinates (longitude, latitude) of the way.
            """

        way_lon_list = []
        way_lat_list = []

        for node_list_num in range(len(node_list)):  # for every node in the node list
            for node in nodes:
                if str(node_list[node_list_num]) == node.getAttribute("id"):
                    # store all nodes of the way into the array
                    way_lon_list.append(node.getAttribute("lon"))
                    way_lat_list.append(node.getAttribute("lat"))
                    break

        # Note: the elements inside way_lon_list now is in the form of ['lon1', 'lon2', .....].
        # So before calculating the average of the longitude and latitude,
        # they should be converted to float with map func.
        way_lon = sum(list(map(float, way_lon_list))) / len(way_lon_list)
        way_lat = sum(list(map(float, way_lat_list))) / len(way_lat_list)

        return way_lon, way_lat

    def check_way_nodes_is_shop(node_list, nodes, keyword_as_supermarket):
        """Use the input list containing way's nodes to check weather any of these nodes is a shop (or a supermarket).
        :param list node_list: A list containing the way's node reference numbers,
        :param nodes: the document node elements from osm xml file,
        :rtype: bool,
        :return: if any node inside is a supermarket.
        """

        contain_shop_node = False

        for node_list_num in range(len(node_list)):  # for every node in the node list
            for node in nodes:
                if str(node_list[node_list_num]) == node.getAttribute("id"):
                    if node.getElementsByTagName("tag"):
                        for node_tag_num in range(len(node.getElementsByTagName("tag"))):
                            if keyword_as_supermarket == 0:
                                if node.getElementsByTagName("tag")[node_tag_num].getAttribute("k") == 'shop':
                                    contain_shop_node = True
                                    break
                            elif keyword_as_supermarket == 1:
                                if node.getElementsByTagName("tag")[node_tag_num].getAttribute("v") == 'supermarket':
                                    contain_shop_node = True
                                    break
                            else:
                                print('keyword_as_supermarket para error. Please check input.')
                                return 0

                    # jump out this loop search and goto next ref in the node list
                    break

        return contain_shop_node

    def check_addr_info_node(node_list, nodes, street, housenumber, name):
        """Use the input list containing way's nodes to check weather any of these nodes meets the standard of the given
        shop.
        :param list node_list: A list containing the way's node reference numbers,
        :param nodes: the document node elements from osm xml file,
        :param str street: the given shop's street,
        :param str housenumber: the given shop's house number,
        :param str name: the given shop's name,
        :rtype: bool,
        :return: if any node inside is the given shop.
        """

        # indicator init
        street_match = False
        housenumber_match = False
        name_match = False

        shop_match = False

        node_is_shop_num = -1  # this indicator can be used to store which node of the way element is a shop

        # If the input housenumber, street or name array is empty for a specific shop
        # (not available from Nominatim), then set it as matched by default.
        if housenumber is None:
            housenumber_match = True
        if street is None:
            street_match = True
        if name is None:
            name_match = True

        breaker = False  # a jump_out indicator

        for node_list_num in range(len(node_list)):  # for every node in the node list
            if breaker:
                break
            for node in nodes:
                if int(node.getAttribute("id")) == int(node_list[node_list_num]):
                    if node.getElementsByTagName("tag"):
                        for nd_num in range(len(node.getElementsByTagName("tag"))):

                            # street match
                            if street is not None:
                                if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'addr:street':
                                    if node.getElementsByTagName("tag")[nd_num].getAttribute("v").lower() == street.lower():
                                        street_match = True

                            # housenumber match
                            if housenumber is not None:
                                if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'addr:housenumber':
                                    if node.getElementsByTagName("tag")[nd_num].getAttribute("v").lower() == housenumber.lower():
                                        housenumber_match = True

                            # Name match for both 'name' and 'brand.'
                            # Here, a small text recognition program is involved to split the full shop's name by .osm
                            # file.
                            # It will loop through all name phrases and try to find a match with the input shop name.
                            # The same for the following brand searching process.
                            if name is not None:
                                if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'name':
                                    for tag_name_split in node.getElementsByTagName("tag")[nd_num].getAttribute("v").lower().split():
                                        for shop_name_split in name.lower().split():
                                            if tag_name_split == shop_name_split:
                                                name_match = True
                                                break

                                if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'brand':
                                    for tag_brand_split in node.getElementsByTagName("tag")[nd_num].getAttribute("v").lower().split():
                                        for shop_name_split in name.lower().split():
                                            if tag_brand_split == shop_name_split:
                                                name_match = True
                                                break

                # the name has to match, or maybe the way just uses another shop's information
                if (name_match and street_match) or (name_match and housenumber_match):
                    shop_match = True

                    # store this node's index for further use
                    node_is_shop_num = node_list_num
                    breaker = True
                    break

        return shop_match, node_is_shop_num

    def check_pure_node(nodes, lon, lat, tlr, street, housenumber, name):
        """Use the whole node set to check weather any of these nodes meets the standard of the given shop.
        :param nodes: The document node elements from osm xml file,
        :param float lon: the longitude of the shop,
        :param float lat: the latitude of the shop,
        :param float tlr: the tolerance of the shop's coordinates,
        :param str street: the given shop's street,
        :param str housenumber: the given shop's house number,
        :param str name: the given shop's name,
        :return: if any node is the given shop and the node itself for further assessment.
        """

        # para init
        shop_match = False
        node_temp = None

        for node in nodes:

            # indicator init
            street_match = False
            housenumber_match = False
            name_match = False
            lon_match = False
            lat_match = False

            geo_match = False

            # If the input housenumber, street or name array is empty for a specific shop
            # (not available from Nominatim), then set it as matched by default.
            if housenumber is None:
                housenumber_match = True
            if street is None:
                street_match = True
            if name is None:
                name_match = True

            # check the geo_coordinates of the node
            lon_match = lon - tlr / 2 <= float(node.getAttribute("lon")) <= lon + tlr / 2
            lat_match = lat - tlr / 3 <= float(node.getAttribute("lat")) <= lat + tlr / 3
            geo_match = lon_match and lat_match

            if geo_match:
                if node.getElementsByTagName("tag"):
                    for nd_num in range(len(node.getElementsByTagName("tag"))):

                        # street match
                        if street is not None:
                            if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'addr:street':
                                if node.getElementsByTagName("tag")[nd_num].getAttribute("v").lower() == street.lower():
                                    street_match = True

                        # housenumber match
                        if housenumber is not None:
                            if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'addr:housenumber':
                                if node.getElementsByTagName("tag")[nd_num].getAttribute("v").lower() == housenumber.lower():
                                    housenumber_match = True

                        # Name match for both 'name' and 'brand.'
                        # Here, a small text recognition program is involved to split the full shop's name by .osm
                        # file.
                        # It will loop through all name phrases and try to find a match with the input shop name.
                        # The same for the following brand searching process.
                        if name is not None:
                            if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'name':
                                for tag_name_split in node.getElementsByTagName("tag")[nd_num].getAttribute("v").lower().split():
                                    for shop_name_split in name.lower().split():
                                        if tag_name_split == shop_name_split:
                                            name_match = True
                                            break

                            if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'brand':
                                for tag_brand_split in node.getElementsByTagName("tag")[nd_num].getAttribute("v").lower().split():
                                    for shop_name_split in name.lower().split():
                                        if tag_brand_split == shop_name_split:
                                            name_match = True
                                            break

                    # the name has to match, or maybe the way just uses another shop's information
                    if name_match:
                        shop_match = True

                        # store this node's index for further use
                        node_temp = node
                        break

        if shop_match is False:
            print('The shop with the given information can not be found. Use a sample shop data instead.')

        return shop_match, node_temp

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

    def get_area(coords, lon_org, lat_org):
        """Return the polygon building area in square meter with the inited coordinates.

        :param list coords: The list of nodes that making of the way, in the form of (n.lon, n.lat),
        :param float lon_org: the longitude of the original point,
        :param float lat_org: the latitude of the original point,
        :return: the building area of the chosen polygon in square meter.
        """

        # translate the input coordinate sets into the cartesian coordinate system with haversine formula
        coords_plate = []
        for n_num in range(0, len(coords)):
            # convert the coordinates into x and y of a cartesian plate system
            x_n = haversine(coords[n_num][0], lat_org, lon_org, lat_org)
            y_n = haversine(lon_org, coords[n_num][1], lon_org, lat_org)

            coords_plate.append((x_n, y_n))

        # area calculating
        area = get_polygon_area(coords_plate)

        return area

    def node_search_from_ref(ref, nodes):
        """Use the input node reference id and return its corresponding node element.
        :param int ref: The node's reference number,
        :param nodes: the dataset of node elements in the .osm file.
        """

        for node in nodes:
            if node.getAttribute("id") == ref:
                return node

    def shop_element_assessment(element):
        """Use the input .osm file element (a node or a way), which represents a shop, to evaluate the shop's
        attraction.
        :param element: The .osm file element, which can be a node or a way and should represent a shop.
        """

        # There is not much information in an .osm file,
        # which can be used to determine how attractive a shop to the customers,
        # not to mention, in order to use it in this program, the information should be common for every shop.
        # Here, four tags which are often used to describe a shop in .osm files, are applied to improve this algorithm,
        # yet they are not always available in a node or a way element.
        # (Wheelchair, toilet for wheelchair, payment methods and opening hours)

        # Therefore, this shop_assessment, as an improvement to the shop attraction algorithm, is barely of use,
        # frankly speaking, but still, I put it here anyway.
        # If in the future version, when any other data sources are involved,
        # maybe the shop_attraction can be calculated more precisely,
        # and the algorithm in this function can be completed.

        # ---------------------------------------------para init-------------------------------------------
        # set default grades as 0.5, the standard grade
        opening_hours_tag = ''  # the shop's opening hour, the longer the opening hour is, the higher the grade is
        definition = {}
        opening_hours_grade = 0.5
        working_hours_week = 1

        wheelchair = False  # weather this shop supports wheelchair
        wheelchair_grade = 0.5

        toilet = False  # weather this shop has a toilet
        toilet_grade = 0.5

        toilet_wheelchair = False  # weather this shop supports accessible toilet
        toilet_factor = 1  # should differ from 1.0 or 2.0, if not support wheelchair, then 1; else 2

        payment = False # weather this shop supports other payment methods, like visa/mastercard/american express
        payment_coin = False
        payment_grade = 0.5

        # Prosperity/Business Circle Index
        # Note: First I wanted to build an index to indicate how close to a business center/living center this shop is,
        # in order to determine the "Passenger Flow Index" of the shop.
        # However, that seemed to be too complex without a solid mathematical models and enough city data.
        # So this part was eventually abandoned.

        # PFI_grade = 0.5
        # BCI_grade = 0.5

        payment_num = 0
        # --------------------------------para init ends-----------------------------------------------
        # -------------------------------data reading -------------------------------------------------
        # loop the element tags for information
        if element.getElementsByTagName("tag"):

            # loop to go through all tags of this element
            for tag_num in range(len(element.getElementsByTagName("tag"))):

                # check if the element has a tag about 'wheelchair'
                if element.getElementsByTagName("tag")[tag_num].getAttribute("k") == 'wheelchair':
                    if element.getElementsByTagName("tag")[tag_num].getAttribute("v") == 'yes':
                        wheelchair = True

                # Normally, there is no tag record showing directly weather a shop has a WC or not.
                # So just read the toilet_wheelchair record.
                # When that record is available, no matter what the value is, I assume there is a usable WC.

                # check toilet_wheelchair
                if element.getElementsByTagName("tag")[tag_num].getAttribute("k") == 'toilets:wheelchair':
                    toilet = True
                    if element.getElementsByTagName("tag")[tag_num].getAttribute("v") == 'yes':
                        toilet_wheelchair = True

                # test if payment method is rich
                if 'payment' in element.getElementsByTagName("tag")[tag_num].getAttribute("k").split(':'):
                    if element.getElementsByTagName("tag")[tag_num].getAttribute("k") == 'payment:coins':
                        # allow coin exchange or all-coins payment? That's unusual.
                        payment_coin = True
                    if element.getElementsByTagName("tag")[tag_num].getAttribute("k") != 'payment:coins' and \
                        element.getElementsByTagName("tag")[tag_num].getAttribute("k") != 'payment:cash':
                        # Besides coin and cash payment, the more paying methods the shop supports, the higher its grade
                        # should be.
                        payment_num += 1

                # test the opening hours
                if element.getElementsByTagName("tag")[tag_num].getAttribute("k") == 'opening_hours':
                    opening_hours_tag = element.getElementsByTagName("tag")[tag_num].getAttribute("v")

                # Here use OpeningHours package to process the complex osm opening_hours string.
                # However, it has trouble processing the time string like "08:00-13:00" without day information.
                # (You will NEVER know what people can type in an .osm tag.)
                if len(opening_hours_tag.split()) == 1:
                    # set the working day
                    opening_hours_tag = f"{'Mo-Fr '}{opening_hours_tag}"

                # if OpeningHours function cannot parse the input working hour string, use standard instead
                try:
                    definition = OpeningHours(opening_hours_tag)
                except Exception as e:
                    print(str(e))
                    print('An error occurred when reading the opening hours tag of the shop. Use standard working'
                          ' time instead.')
                    # set a standard working hours
                    definition = OpeningHours('Mo-Fr 09:00-20:00')

        # -------------------------------data reading ends --------------------------------------------
        # -------------------------------data process -------------------------------------------------
        # end of the data-reading process, and now analyze the information and try to give grades
        # opening_hours relevant
        if definition != {}:
            working_hours_week = 0
            for day in ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']:
                # calculate all working minutes in a week
                if definition.opening_hours[day]:
                    working_hours_week += definition.opening_hours[day][0][1] - definition.opening_hours[day][0][0]
            working_hours_week = working_hours_week / 60

        # every 10 hours is a rank, and a weekly basic working hour is 55h
        opening_hours_rank = (working_hours_week - 55) // 10
        opening_hours_grade = opening_hours_grade + opening_hours_rank * 0.05

        # the grade cannot be lower than 0, but can be higher than 1. So here a limit is necessary
        if opening_hours_grade > 1:
            opening_hours_grade = 1

        # wheelchair relevant
        if wheelchair:
            wheelchair_grade = 1

        # toilet relevant
        if toilet:
            toilet_grade = 1

        if toilet_wheelchair:
            toilet_factor = 2

        toilet_grade = toilet_grade * toilet_factor

        if payment_coin:
            payment_grade += 0.05
        payment_grade += payment_num * 0.05

        if payment_grade > 1:
            payment_grade = 1

        # -------------------------------data process ends---------------------------------------------

        # final grade of the shop (if these factors are available)
        grade = payment_grade * toilet_grade * wheelchair_grade * opening_hours_grade

        # test how far away the grade is from standard 0.5^4
        # here use a log function to minimize the factor's influence
        grade_coefficient = np.log(grade / 0.5 / 0.5 / 0.5 / 0.5) + 1

        return grade_coefficient

    def determine_shop_node_boundary(node_lon, node_lat, nodes, ways, lon_org, lat_org):
        """This function can be used to determine a shop node's boundary, but it is not recommended to use for its
        high time and resource consuming.

        The main principle is to use the shop's node's coordinates as basic,
        and try to loop for all ways in the given .osm file to find the smallest way, which surrounds this node
        geographically and then set the way as the shop's boundary.

        However, this method is actually not accurate and sometimes can have massive error.
        So please use other alternative methods if there are some.
        :param float node_lon: The longitude of the shop node,
        :param float node_lat: the latitude of the shop node,
        :param nodes: all node set inside the given .osm file,
        :param ways: all way set inside the given .osm file,
        :param float lon_org: the origin point's longitude of the .osm file, manually set as the left-bottem point,
        :param float lat_org: the origin point's latitude of the .osm file, manually set as the left-bottem point.

        :return: The smallest way's building area, which can contain the shop node

        """

        # para init
        way_ref_meet_condition = []  # this list is used to store the ways, which can contain the shop node
        way_cord_meet_condition = []

        # search for all ways for matches
        for way in ways:

            # a way with a area has to have at least 3 nodes(triangle)
            if len(way.getElementsByTagName("nd")) >= 3:

                way_node_list = []
                cord_list = []

                if way.getElementsByTagName("nd"):
                    for nd_num in range(len(way.getElementsByTagName("nd"))):
                        # write the way's node reference number into the node_list array
                        way_node_list.append(way.getElementsByTagName("nd")[nd_num].getAttribute("ref"))

                # convert the node_ref into coordinates
                cord_list = get_way_nodes_coordinates_with_ref(way_node_list, nodes)

                polygon_way = Polygon(cord_list)
                point_node = Point(node_lon, node_lat)

                # store the ways' ref id, for later finding the smallest way's area
                if polygon_way.contains(point_node):
                    way_cord_meet_condition.append(cord_list)
                    way_ref_meet_condition.append(way.getAttribute("id"))

        way_smallest_area = 0
        way_temp = None

        if len(way_cord_meet_condition) > 0:
            way_smallest_area = get_area(way_cord_meet_condition[0], lon_org, lat_org)
            area = 0
            way_id = 0
            for way_num in range(1, len(way_cord_meet_condition)):
                area = get_area(way_cord_meet_condition[way_num], lon_org, lat_org)

                # store the smallest way's data
                if area < way_smallest_area:
                    way_smallest_area = area
                    way_id = way_ref_meet_condition[way_num]

            # also get the way meet the standard for way assessment
            for way in ways:
                if way.getAttribute("id") == way_id:
                    way_temp = way
        else:
            print('No matched way containing this shop node. Please use standard data instead.')

        return way_smallest_area, way_temp

    # --------------------------------------end inner function zone-----------------------------

    # read osm file as xml format
    DOMTree = xml.dom.minidom.parse(osm_file)
    osm = DOMTree.documentElement

    # import all way and node elements
    ways = osm.getElementsByTagName("way")
    nodes = osm.getElementsByTagName("node")

    # area store array init
    factor_list = []
    area_list = []

    for shop_num in range(len(lon_list)):  # search for every shop record

        print(f"Searching for the {str(shop_num+1)}st shop's information in .osm file, total {len(lon_list)} shops.")

        # the area and influence of the shop's infrastructure, and will be directly applied to the building area
        # of the shop
        area = 0
        factor = 1

        # Theoretically, nodes make of ways in an .osm file.
        # But a node does not have to make of ways,
        # and that means there could be isolated nodes that are not part of a way or a relationship.
        # So we should search not only ways, but also nodes for shop information.
        # However, in the osm files I tested, almost all shops can be found by a way element or a sub-element of a way
        # (that means a node), so we can get rid of node-searching and focus on ways (and their sub-elements) only.

        # Update: in case some shops are still not available by way searching only, a pure node-searching is added.
        for way in ways:  # search for every way

            # indicator and store array init
            is_shop = False  # indicates weather this way is a shop or not
            node_list = []

            # check if the way have tags or not
            if way.getElementsByTagName("tag"):
                for tag_num in range(len(way.getElementsByTagName("tag"))):  # loop to search for all tags in this way

                    if keyword_as_supermarket == 1:
                        if way.getElementsByTagName("tag")[tag_num].getAttribute("v") == 'supermarket':
                            is_shop = True  # set the indicator as ture

                            # store this way's node reference number for further use
                            for nd_num in range(len(way.getElementsByTagName("nd"))):
                                # write the way's node reference number into the node_list array
                                node_list.append(way.getElementsByTagName("nd")[nd_num].getAttribute("ref"))

                    elif keyword_as_supermarket == 0:

                        # This time, only "key"="shop" is needed, while the "value" is not specified.
                        if way.getElementsByTagName("tag")[tag_num].getAttribute("k") == 'shop':
                            is_shop = True  # set the indicator as ture

                            # store this way's node reference number for further use
                            for nd_num in range(len(way.getElementsByTagName("nd"))):
                                # write the way's node reference number into the node_list array
                                node_list.append(way.getElementsByTagName("nd")[nd_num].getAttribute("ref"))
                    else:
                        print('keyword_as_supermarket error. Please check your input.')
                        return 0

            else:
                if check_node == 1:

                    # store list init
                    node_list = []

                    if way.getElementsByTagName("nd"):  # theoretically, a way must have node inside, or?
                        for nd_num in range(len(way.getElementsByTagName("nd"))):

                            # write the way's node reference number into the node_list array
                            node_list.append(way.getElementsByTagName("nd")[nd_num].getAttribute("ref"))

                        # check if any node of the way is a shop
                        is_shop = check_way_nodes_is_shop(node_list, nodes, keyword_as_supermarket)
                else:
                    pass

            # if it comes to this step, then either the way has a shop tag,
            # or at least one node of the way has a shop tag.
            if is_shop:

                # indicator init
                geo_match = False  # indicates weather the center of the way is in the matching area or not (+- tlr)

                name_match = False  # indicates weather the name tags of the way meets a shop match

                # geo_match check if the center of the way is in the tolerance (about 10m)
                geo_match_lon = lon_list[shop_num] - tlr / 2 <= cal_way_center(node_list, nodes)[0] <= \
                                lon_list[shop_num] + tlr / 2
                geo_match_lat = lat_list[shop_num] - tlr / 3 <= cal_way_center(node_list, nodes)[1] <= \
                                lat_list[shop_num] + tlr / 3

                geo_match = geo_match_lon and geo_match_lat

                shop_match = False

                if geo_match:
                    # name_match indicates weather this shop way (or its sub node) matches the address information from
                    # the given array.

                    # indicator for way & node init
                    way_match = False
                    node_match = False

                    # way sub indicators init
                    street_match = False
                    name_match = False
                    housenumber_match = False

                    # If the input housenumber, street or name array is empty for a specific shop
                    # (not available from Nominatim), then set it as matched by default.
                    if housenumber_list[shop_num] is None:
                        housenumber_match = True
                    if street_list[shop_num] is None:
                        street_match = True
                    if name_list[shop_num] is None:
                        name_match = True

                    if way.getElementsByTagName("tag"):  # check the way element itself
                        for nd_num in range(len(way.getElementsByTagName("tag"))):

                            # street match
                            if street_list[shop_num] is not None:
                                if way.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'addr:street':
                                    if way.getElementsByTagName("tag")[nd_num].getAttribute("v").lower() == \
                                            street_list[shop_num].lower():
                                        street_match = True

                            # housenumber match
                            if housenumber_list[shop_num] is not None:
                                if way.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'addr:housenumber':
                                    if way.getElementsByTagName("tag")[nd_num].getAttribute("v").lower() == \
                                            housenumber_list[shop_num].lower():
                                        housenumber_match = True

                            # Name match for both 'name' and 'brand.'
                            # Here, a small text recognition program is involved to split the full shop's name by .osm
                            # file.
                            # It will loop through all name phrases and try to find a match with the input shop name.
                            # The same for the following brand searching process.
                            if name_list[shop_num] is not None:
                                if way.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'name':
                                    for tag_name_split in way.getElementsByTagName("tag")[nd_num].getAttribute("v").lower().split():
                                        for shop_name_split in name_list[shop_num].lower().split():
                                            if tag_name_split == shop_name_split:
                                                name_match = True
                                                break

                                if way.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'brand':
                                    for tag_brand_split in way.getElementsByTagName("tag")[nd_num].getAttribute("v").lower().split():
                                        for shop_name_split in name_list[shop_num].lower().split():
                                            if tag_brand_split == shop_name_split:
                                                name_match = True
                                                break

                        # If name_match and either of the other two is matched, then set way_match as true.
                        # If it is another same-named shop happened to be on another street with the same housenumber,
                        # the geo-coordinates should differ.
                        # If the name is not matched but the other two are matched, then the way could be a shopping
                        # mall with different shops, and they share a common street and housenumber.

                        # After test, this condition should be changed to only name_match,
                        # because if and only if geo and name are matched together, a shop can be determined.

                        # if (name_match and street_match) or (name_match and housenumber_match):
                        if name_match:
                            way_match = True

                        # Here, use the shop's tag information to complete the rating system. The way_match condition is
                        # placed here because the tags of the shop are available in the way element.
                        if way_match:

                            # evaluate the shop way
                            factor = shop_element_assessment(way)

                    # the way does not provide tag information, and we have to dig deeper into its consisting nodes' tag
                    else:

                        node_match, node_num = check_addr_info_node(node_list, nodes, street_list[shop_num], housenumber_list[shop_num], name_list[shop_num])

                        # Likewise, the tags are reachable in one of the way's nodes.
                        # So the judgment should be placed here.
                        if node_match:
                            if node_num != -1:

                                # evaluate the shop node
                                factor = shop_element_assessment(node_search_from_ref(node_list[node_num], nodes))

                    if way_match or node_match:
                        shop_match = True

                if shop_match and geo_match:
                    area = get_area(get_way_nodes_coordinates_with_ref(node_list, nodes), lon_org, lat_org)
                    break

        # If the program goes this far and has not been jumped out of the loop,
        # then it means the program did not find any match after searching all ways and their sub nodes.
        # So now we simply search for all nodes for match.
        if area == 0 and factor == 1:
            print('The shop is not available in .osm file\'s ways. Searching simple nodes instead.')
            node_find_match, node_temp = check_pure_node(nodes, lon_list[shop_num], lat_list[shop_num], tlr, street_list[shop_num], housenumber_list[shop_num], name_list[shop_num])

            if predict_node_boundary == 1:
                print('Trying to use the smallest way containing the shop node as shop\'s building area.')

                # if the node_searching_program has found a matched shop node
                if node_find_match:
                    area_smallest_match, way_smallest_match = determine_shop_node_boundary(float(node_temp.getAttribute("lon")), float(node_temp.getAttribute("lat")),
                                             nodes, ways, lon_org, lat_org)

                    # if the determine_shop_node_boundary function has found a matched way
                    if area_smallest_match != 0:
                        area = area_smallest_match
                        factor = shop_element_assessment(way_smallest_match)
                    # if the determine_shop_node_boundary has not found any matched way
                    else:
                        area = 80.00
                        factor = shop_element_assessment(node_temp)

                # if the node_searching_program has not found any matched shop node
                else:
                    print('One of your input shop record seems not available in .osm file. Use standard data instead.')
                    # the area of a node is always 0, so use a standard shop building area, 80m^2 instead
                    area = 80.00
                    factor = 1
            else:
                print('Use standard building area as shop\'s area.')

                if node_find_match:
                    area = 80.00
                    factor = shop_element_assessment(node_temp)
                else:
                    area = 80.00
                    factor = 1

            area_list.append(area)
            factor_list.append(factor)
        else:
            # the information was already found by way_searching
            area_list.append(area)
            factor_list.append(factor)

        # for testing only
        print(f'shop building area {str(area)} added.')
        print(f'shop attraction {str(factor)} added.')
        print('----------------------')

    return area_list, factor_list


# # test code
# get_shop_way_ref_osm(10.46843, 52.25082)
# pass
