import numpy as np
import pandas as pd
import osmium


def get_shop_info_osm(lon, lat, bbox,
                  osm_file="C:/Users/86781/PycharmProjects/pythonProject/data/osm/germany-latest.osm.pbf",
                  xlsx_file="C:/Users/86781/PycharmProjects/pythonProject/data/test_area_shops.xlsx"):
    """This function is used to get the shop information from .osm.pbf file, in order to calculate their attractions
     in the following steps. The longitude and latitude should be able to be found in the .xlsx file, which was
     generated before by a script using Nominatim service or an .osm.pbf traversal program.
     :param float lon: The centre longitude of the shop,
     :param float lat: the centre latitude of the shop,
     :param float bbox: the offset of the coordinates, default as 0.003, it is about 0,3km from the german region,
     :param str osm_file: the .osm.pbf file, in which the shops' information is stored,
     :param str xlsx_file: the .xlsx file, generated from former script, containing geo-coordinates of the shops,
     :return: TBD,
     :rtype: TBD.
    """

    pass
