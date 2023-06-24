import osmium
import pandas as pd

class shopHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.shop_list = []
        self.shop_lon = []
        self.shop_lat = []
    def node(self, n):
        if 'supermarket' in n.tags:
            if 'addr:housenumber' in n.tags and 'addr:street' in n.tags and 'addr:city' in n.tags and 'name' in n.tags:
                self.shop_list.append(n.tags['addr:housenumber'])
                self.shop_lon.append(n.location.lon)
                self.shop_lat.append(n.location.lat)

    def way(self, w):
        pass

    def relation(self, r):
        pass



def get_shop_list_osm(osm_file='C:/Users/86781/PycharmProjects/pythonProject/data/test_area.osm'):
    """This function can be used to generate a shop list inside the test area, using .pnf extracted .osm file.
    Because the input .osm file is already in the size of the chosen test area, so no bounding boxes or geo-filters
    are needed here.
    :param str osm_file: The osm file containing test area data, extracted from the corresponding .pbf file.
    """


