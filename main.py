import sys
from osm_object_Methods.Find_Coordinates import get_one_node_coordinates
from osm_object_Methods.Find_Coordinates import get_one_way_coordinates
from osm_object_Methods.Find_Coordinates import get_multi_ways_coordinates

if __name__ == '__main__':

    path = 'C:/Users/86781/PycharmProjects/pythonProject/data/osm/germany-latest.osm.pbf'

    search_name = 'Rewe'
    search_street = 'Rugenbarg'
    search_housenumber = '7'
    search_city = 'Hamburg'


    waylist = [['Freibad Quickborn', '13', 'Am Freibad', 'Quickborn'],
               ['Bürgerzentrum Südstadt', '10', 'Henriette-Obermüller-Straße', 'Karlsruhe']]



    Address = get_one_way_coordinates(search_city, search_street, search_housenumber, search_name, path)
    # Address = get_multi_ways_coordinates(waylist, path)

    print(type(Address))
    print(Address)
    print('end')
    sys.exit(0)
