import os.path
import pandas as pd
import openpyxl
import sys
import osmium


class find_node_with_ref(osmium.SimpleHandler):

    def __init__(self, ref_num, bbox):
        osmium.SimpleHandler.__init__(self)
        self.ref_num = ref_num
        self.bbox = bbox

    # def node(self, n):
        # if n.id ==


class Gather_Information_Handler(osmium.SimpleHandler):
    """This method can be used to match the given address to the coordinates in an osm.pbf file. However, due to the
    algorithm and hardware strength, the efficiency won't be good enough, so it may take hours to find the POIs.
    A Possible alternative is to use the Nominatim service on a server.

    It is worth noting that the osm nodes with the right city, street and housenumber, which are found with the methods
    just mentioned before, could differ from the nodes, ways and relations of warehouse and shops in an osm.pbf file,
    which contains the information we need. In such situations, a bounding box should be set after finding the nodes
    with actual address, and should be based on the coordinates of the nodes. Then the information should be passed to
    another method to find the right shop nodes containing the information.

    Sometimes the matched objects in an osm.pbf file are ways or relations, rather than nodes. It is possible that the
    ways and relations already contain all the information of the shops. So

    +-0.015
    """

    def __init__(self, keyword_city, keyword_street, keyword_housenumber, keyword_name):
        osmium.SimpleHandler.__init__(self)
        self.address = None
        self.locations = []
        self.bounding_box = []

        self.searching_name_city = keyword_city
        self.searching_name_street = keyword_street
        self.searching_name_housenumber = keyword_housenumber
        self.searching_name_name = keyword_name

    def node(self, n):
        """A node is simple: It could be a separate shop with its own housenumber, or it could also be a store in a
        shopping mall. It has its own coordinates, so the coordinates are stored here for further use. (Sometimes the
        node with shop name but the information is in other ways objects, so a second searching with bounding box
        is needed.) The bounding box is set to be a square, [lon-0.015,lat-0.015,lon+0.015,lat+0.015]. In the
        lag-direction is about 1.7km."""
        if 'addr:street' in n.tags and 'addr:housenumber' in n.tags and 'addr:city' in n.tags and 'name' in n.tags:

            city_match = False
            street_match = False
            housenumber_match = False
            name_match = False

            # other elements should be matched, while the name should just in the node tag
            street_match = self.searching_name_street == n.tags['addr:street']
            housenumber_match = self.searching_name_housenumber == n.tags['addr:housenumber']
            city_match = self.searching_name_city == n.tags['addr:city']
            name_match = self.searching_name_name in n.tags['name'].split()

            if street_match and housenumber_match and city_match:
                if name_match:
                    print('Node match. Geo coordinates stored.')
                    self.address = (n.tags['addr:street'], n.tags['addr:housenumber'], n.location.lon, n.location.lat)
                    self.bounding_box = [n.location.lon-0.015, n.location.lat-0.015, n.location.lon+0.015,
                                         n.location.lat+0.015]
                else:
                    # The name does not match, while city, street and housenumber match;
                    print('Node name does not match, but geo coordinates are stored anyway.')
                    self.address = (n.tags['addr:street'], n.tags['addr:housenumber'], n.location.lon, n.location.lat)
                    self.bounding_box = [n.location.lon - 0.015, n.location.lat - 0.015, n.location.lon + 0.015,
                                         n.location.lat + 0.015]

    def way(self, w):
        """
        A way does not have coordinates; instead, it was shaped by a list of nodes that has their own coordinates.
        Some ways objects do not have housenumber or even street string in their tags, so the matching conditions are
        therefore loosed accordingly. """
        if 'addr:street' in w.tags and 'addr:housenumber' in w.tags and 'addr:city' in w.tags and 'name' in w.tags:

            city_match = False
            street_match = False
            housenumber_match = False
            name_match = False

            street_match = self.searching_name_street == w.tags['addr:street']
            housenumber_match = self.searching_name_housenumber == w.tags['addr:housenumber']
            city_match = self.searching_name_city == w.tags['addr:city']
            name_match = self.searching_name_name in w.tags['name'].split()

            # check if the way is closed.
            # TODO

            if name_match and city_match and street_match:
                if housenumber_match:
                    print('Way match. Nodes references stored.')

            if street_match and housenumber_match and city_match:
                if name_match:
                    print('Way match. Geo coordinates stored.')
                    self.address = (w.tags['addr:street'], w.tags['addr:housenumber'], w.location.lon, w.location.lat)
                else:
                    # The name does not match, while city, street and housenumber match;
                    print('The name does not match, but the geo coordinates are stored anyway.')
                    self.address = (w.tags['addr:street'], w.tags['addr:housenumber'], w.location.lon, w.location.lat)

    def relation(self, r):
        if 'addr:street' in r.tags and 'addr:housenumber' in r.tags and 'addr:city' in r.tags and 'name' in r.tags:

            city_match = False
            street_match = False
            housenumber_match = False
            name_match = False

            street_match = self.searching_name_street == r.tags['addr:street']
            housenumber_match = self.searching_name_housenumber == r.tags['addr:housenumber']
            city_match = self.searching_name_city == r.tags['addr:city']
            name_match = self.searching_name_name in r.tags['name'].split()

            if street_match and housenumber_match and city_match:
                if name_match:
                    self.address = (r.tags['addr:street'], r.tags['addr:housenumber'], r.location.lon, r.location.lat)
                else:
                    # The name does not match, while city, street and housenumber match;
                    print('The name does not match, but the geo coordinates are stored anyway.')
                    # self.address = (n.tags['addr:street'], n.tags['addr:housenumber'], n.location.lon, n.location.lat)
