import osmium


def get_multicoordinate_from_multiaddress(address_list, pbf_file):
    """
    Get the coordinates lists from the address list, using local .pbf file and python packages for searching.
    :param list address_list: A list of address which should be the form of address_list[num] = [housenumber, street, city, name],
    :param str pbf_file: the to-be-searched .pbf file,
    :return coordinates: the coordinates of the to-be-searched address,
     in the form of coordinates[num] = [lon, lat],
    :return bounding_box: the bounding box of the to-be-searched address,
     in the form of bounding_box[num] = [min_lon, min_lat, max_lon, max_lat].
    """

    # para init
    coordinates = []
    bounding_box = []

    for num in range(0, len(address_list)):
        GCA = get_coordinate_from_address(address_list[num][0], address_list[num][1], address_list[num][2], address_list[num][3])
        GCA.apply_file(pbf_file)

        coordinates.append([GCA.address[2], GCA.address[3]])
        bounding_box.append([GCA.bounding_box[0], GCA.bounding_box[1], GCA.bounding_box[2], GCA.bounding_box[3]])

    return coordinates, bounding_box


class get_coordinate_from_address(osmium.SimpleHandler):
    """This method can be used to match the given address to the coordinates in an osm.pbf file. However, due to the
    algorithm and hardware strength, the efficiency won't be good enough, so it may take hours to find the POIs.
    A Possible alternative is to use the Nominatim service on a server.

    It is worth noting that the osm nodes with the right city, street and housenumber, which are found with the methods
    just mentioned before, could differ from the nodes, ways and relations of warehouse and shops in an osm.pbf file,
    which contains the information we need. In such situations, a bounding box should be offered after finding the nodes
    with actual address, and the bounding box should be based on the coordinates of the nodes. Then the information
    should be passed to further methods for detailed information.

    Sometimes the matched objects in an osm.pbf file are ways or relations, rather than nodes. It is possible that the
    ways and relations already contain all the information of the shops. So only the basic searching is applied under
    such occasions.

    The allowable offset is set to 0.003, and is applied to the bounding box.
    """

    def __init__(self, keyword_housenumber, keyword_street, keyword_city, keyword_name):
        """
        :param str keyword_city: the to-be-searched city keyword,
        :param str keyword_street: the to-be-searched street keyword,
        :param str keyword_housenumber: the to-be-searched housenumber keyword,
        :param str keyword_name: the to-be-searched name keyword,
        :return: the address of the element and its bounding box.
        """
        osmium.SimpleHandler.__init__(self)
        self.address = None
        self.locations = []
        self.bounding_box = []

        self.searching_name_city = keyword_city
        self.searching_name_street = keyword_street
        self.searching_name_housenumber = keyword_housenumber
        self.searching_name_name = keyword_name

    def node(self, n):
        """
        A node is simple: It could be a separate shop with its own housenumber, or it could also be a store in a
        shopping mall. It has its own coordinates, so the coordinates are stored here for further use. (Sometimes the
        node with shop name but the information is in other ways objects, so a second searching with bounding box
        is needed.) The bounding box is set to be a square, [lon-0.003,lat-0.003,lon+0.003,lat+0.003]. In the
        lat-direction is about 0.3km from the German region.
        :param n: Node.
        """

        if 'addr:street' in n.tags and 'addr:housenumber' in n.tags and 'addr:city' in n.tags and 'name' in n.tags:

            # other elements should be matched, while the name should just in the node tag
            street_match = self.searching_name_street == n.tags['addr:street']
            housenumber_match = self.searching_name_housenumber == n.tags['addr:housenumber']
            city_match = self.searching_name_city == n.tags['addr:city']
            name_match = self.searching_name_name in n.tags['name'].split()

            if street_match and housenumber_match and city_match:
                if name_match:
                    print('Node match. Geo coordinates stored.')
                    self.address = (n.tags['addr:street'], n.tags['addr:housenumber'], n.location.lon, n.location.lat)
                    self.bounding_box = [n.location.lon - 0.003, n.location.lat - 0.003, n.location.lon + 0.003,
                                         n.location.lat + 0.003]
                    # then jump out the method
                else:
                    # The name does not match, while city, street and housenumber match;
                    print('Node name does not match, but geo coordinates are stored anyway.')
                    self.address = (n.tags['addr:street'], n.tags['addr:housenumber'], n.location.lon, n.location.lat)
                    self.bounding_box = [n.location.lon - 0.003, n.location.lat - 0.003, n.location.lon + 0.003,
                                         n.location.lat + 0.003]

    def way(self, w):
        """
        A way does not have coordinates; instead, it was shaped by a list of nodes that has their own coordinates.
        Some ways objects do not have housenumber or even street string in their tags, so the matching conditions are
        therefore loosed accordingly.
        :param w: Way.
        """

        if 'addr:street' in w.tags and 'addr:housenumber' in w.tags and 'addr:city' in w.tags and 'name' in w.tags:

            street_match = self.searching_name_street == w.tags['addr:street']
            housenumber_match = self.searching_name_housenumber == w.tags['addr:housenumber']
            city_match = self.searching_name_city == w.tags['addr:city']
            name_match = self.searching_name_name in w.tags['name'].split()

            # check if the way is closed.
            # TODO

            if street_match and housenumber_match and city_match:
                if name_match:
                    print('Way match. Geo coordinates stored.')
                    self.address = (w.tags['addr:street'], w.tags['addr:housenumber'], w.location.lon, w.location.lat)
                    self.bounding_box = [w.location.lon - 0.003, w.location.lat - 0.003, w.location.lon + 0.003,
                                         w.location.lat + 0.003]
                else:
                    # The name does not match, while city, street and housenumber match;
                    print('The name does not match, but the geo coordinates are stored anyway.')
                    self.address = (w.tags['addr:street'], w.tags['addr:housenumber'], w.location.lon, w.location.lat)
                    self.bounding_box = [w.location.lon - 0.003, w.location.lat - 0.003, w.location.lon + 0.003,
                                         w.location.lat + 0.003]

    def relation(self, r):
        """
        In an .osm file, a shop is not likely to be presented as a relation, because normally, relations contain
        several way elements and that is somehow too big for a shop description. So here only the basic searching is
        used and only fit for the relations that have 'street', 'housenumber', 'city' and 'name' tags together.
        :param r: Relation.
        """

        if 'addr:street' in r.tags and 'addr:housenumber' in r.tags and 'addr:city' in r.tags and 'name' in r.tags:

            street_match = self.searching_name_street == r.tags['addr:street']
            housenumber_match = self.searching_name_housenumber == r.tags['addr:housenumber']
            city_match = self.searching_name_city == r.tags['addr:city']
            name_match = self.searching_name_name in r.tags['name'].split()

            if street_match and housenumber_match and city_match:
                if name_match:
                    self.address = (r.tags['addr:street'], r.tags['addr:housenumber'], r.location.lon, r.location.lat)
                    self.bounding_box = [r.location.lon - 0.003, r.location.lat - 0.003, r.location.lon + 0.003,
                                         r.location.lat + 0.003]
                else:
                    # The name does not match, while city, street and housenumber match;
                    print('The name does not match, but the geo coordinates are stored anyway.')
                    self.address = (r.tags['addr:street'], r.tags['addr:housenumber'], r.location.lon, r.location.lat)
                    self.bounding_box = [r.location.lon - 0.003, r.location.lat - 0.003, r.location.lon + 0.003,
                                         r.location.lat + 0.003]
