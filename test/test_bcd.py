import osmium
from math import radians, sin, cos, sqrt, atan2

def haversine(lon1, lat1, lon2, lat2):

    # approximate radius of earth in km
    R = 6373.0

    lon1 = radians(lon1)
    lat1 = radians(lat1)
    lon2 = radians(lon2)
    lat2 = radians(lat2)

    diff_lon = lon2 - lon1
    diff_lat = lat2 - lat1

    a = sin(diff_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(diff_lon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance

distance = haversine(10.52, 52.26, 10.52, 52.2603)
pass

#
# class ShopAreaHandler(osmium.SimpleHandler):
#     def __init__(self, keyword_name, keyword_housenumber, keyword_street, lon_org, lat_org):
#
#         osmium.SimpleHandler.__init__(self)
#
#         # para init
#         self.searching_name_street = keyword_street
#         self.searching_name_housenumber = keyword_housenumber
#         self.searching_name_name = keyword_name
#         self.lon_org = lon_org
#         self.lat_org = lat_org
#
#         self.total_area = 0
#
#     def area(self, coords):
#
#         # area calculating
#         return 0.5 * sum(x0 * y1 - x1 * y0 for ((x0, y0), (x1, y1)) in zip(coords, coords[1:] + [coords[0]]))
#
#     def way(self, w):
#         if 'shop' in w.tags:
#
#
#         if 'building' in w.tags:
#             # self.building = [(n.lon, n.lat) for n in w.nodes]
#
#
#             # change the geo-coordinates into 2-D plane coordinate system coordinates
#             coords = [(n.lon, n.lat) for n in w.nodes]
#             self.total_area += abs(self.area(coords))
#
#
#
#
# SAH = ShopAreaHandler('abc', '63', 'Rebenring', 'braunschweig')
# SAH.apply_file("D:/test/braun-part.osm")
# print(SAH.total_area)