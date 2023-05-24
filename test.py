# import osmium
#
# class CityExtractor(osmium.SimpleHandler):
#     def __init__(self, city_name):
#         osmium.SimpleHandler.__init__(self)
#         self.city_boundaries = []
#         self.city_keyword = city_name
#     def way(self,w):
#         if self.city_keyword in w.tags:
#             self.city_boundaries.append(w)
#     def relation(self,r):
#         if self.city_keyword in r.tags:
#             self.city_boundaries.append(r)
#
# if __name__ == '__main__':
#     city_name = 'Braunschweig'
#     path = 'C:/Users/86781/PycharmProjects/pythonProject/venv/data/osm/germany-latest.osm.pbf'
#
#     city_extractor = CityExtractor(city_name)
#     city_extractor.apply_file(path)
#
#     print(type(city_extractor))
#     print(city_extractor)



#
# from pyrosm import OSM
# from pyrosm import get_data
#
# path = "C:/Users/86781/PycharmProjects/pythonProject/venv/data/osm/germany-latest.osm.pbf"
# # fp = get_data(path)
# osm = OSM(path)
#
# # Read all boundaries using the default settings
# boundaries = osm.get_boundaries(name="Braunschweig")
# boundaries.plot(facecolor="none", edgecolor="blue")




#
# import osmium
# import shapely.wkb
# import pandas as pd
# import geopandas as gpd
#
# region = "ukraine"
#
#
# def merge_two_dicts(x, y):
#     z = x.copy()  # start with keys and values of x
#     z.update(y)  # modifies z with keys and values of y
#     return z
#
#
# class AdminAreaHandler(osmium.SimpleHandler):
#     def __init__(self):
#         osmium.SimpleHandler.__init__(self)
#
#         self.areas = []
#         self.wkbfab = osmium.geom.WKBFactory()
#
#     def area(self, a):
#         if "admin_level" in a.tags:
#             wkbshape = self.wkbfab.create_multipolygon(a)
#             shapely_obj = shapely.wkb.loads(wkbshape, hex=True)
#
#             area = {"id": a.id, "geo": shapely_obj}
#             area = merge_two_dicts(area, a.tags)
#
#             self.areas.append(area)
#
#
# handler = AdminAreaHandler()
#
# # path to file to local drive
# # download from https://download.geofabrik.de/index.html
# osm_file = "C:/Users/86781/PycharmProjects/pythonProject/venv/data/osm/germany-latest.osm.pbf"
#
# # start data file processing
# handler.apply_file(osm_file, locations=True, idx='flex_mem')
#
# df = pd.DataFrame(handler.areas)
# gdf = gpd.GeoDataFrame(df, geometry="geo")
# gdf



import osmium
import numpy as np
from shapely.geometry import shape
import shapely.wkb as wkblib
import osm2geojson
from shapely.geometry import Polygon

class nodeSearching(osmium.SimpleHandler):
    def __init__(self,id_list):
        osmium.SimpleHandler.__init__(self)
        self.id_list = id_list
        self.node_position = []

    def node(self, n):
        for node_num in range(0,len(self.id_list)):
            if n.id == self.id_list[node_num]:
                self.node_position.append((n.id, n.location.lon, n.location.lat))


class buildingHandler(osmium.SimpleHandler):
    def __init__(self, city_keyword, street_keyword, housenumber_keyword):
        osmium.SimpleHandler.__init__(self)
        self.count = 0
        self.city = city_keyword
        self.street = street_keyword
        self.housenumber = housenumber_keyword
        self.nodes_id = []

    def way(self, w):
        if 'addr:city' in w.tags and 'addr:street' in w.tags and 'addr:housenumber' in w.tags:
            if w.tags['addr:city'] == self.city and w.tags['addr:street'] == self.street and w.tags['addr:housenumber'] == self.housenumber:
                if 'brand' in w.tags and w.tags['brand'] == 'REWE':
                    self.nodes_id = np.zeros(len(w.nodes))
                    for ref_num in range(0, len(w.nodes)):
                        self.nodes_id[ref_num] = w.nodes[ref_num].ref
        self.count += 1
        if self.count % 10000 == 0:
            print(f'{self.count} ways processed.')



city_keyword = "Hamburg"
street_keyword = "Tibarg"
housenumber_keyword = "32"

path = "C:/Users/86781/PycharmProjects/pythonProject/data/osm/hamburg-latest.osm.pbf"

bH = buildingHandler(city_keyword, street_keyword, housenumber_keyword)
bH.apply_file(path)

nS = nodeSearching(bH.nodes_id)
nS.apply_file(path)

way_points = nS.node_position
polygon = Polygon(way_points)
print(polygon.area)




#
# for b in bH.building:
#     geom = shape(b.geojson())
#     print(geom.area)
