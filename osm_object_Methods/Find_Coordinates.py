import osmium
import numpy as np


def get_one_way_coordinates(city, street, housenumber, name, filepath):

    # step 1: find the way list containing the node references
    ACW = AddressToCoordinatesWayHandler(city, street, housenumber, name)
    ACW.apply_file(filepath)
    nodes_id = ACW.nodes_id

    # step 2: find the way nodes' coordinates based on the node references
    NSL = NodeSearchingFromWay(nodes_id)
    NSL.apply_file(filepath)

    avg_lon = 0
    avg_lat = 0

    # calculate the center point of the way and give that out
    for num in range(0, len(NSL.node_position)):
        avg_lon += NSL.node_position[num][1]
        avg_lat += NSL.node_position[num][2]
    avg_lon = avg_lon / len(NSL.node_position)
    avg_lat = avg_lat / len(NSL.node_position)

    return [avg_lon, avg_lat]


class NodeSearchingFromWay(osmium.SimpleHandler):
    def __init__(self, id_list):
        osmium.SimpleHandler.__init__(self)
        self.id_list = id_list
        self.node_position = []
        self.count = 0

    def node(self, n):
        for node_num in range(0, len(self.id_list)):
            if n.id == self.id_list[node_num]:
                self.node_position.append((n.id, n.location.lon, n.location.lat))
        self.count += 1
        if self.count % 1000000 == 0:
            print(f'{self.count} nodes processed.')


class AddressToCoordinatesWayHandler(osmium.SimpleHandler):

    def __init__(self, keyword_city, keyword_street, keyword_housenumber, keyword_name):
        osmium.SimpleHandler.__init__(self)
        self.count = 0
        self.nodes_id = []

        self.searching_name_city = keyword_city
        self.searching_name_street = keyword_street
        self.searching_name_housenumber = keyword_housenumber
        self.searching_name_name = keyword_name

    def way(self, w):
        if 'addr:street' in w.tags and 'addr:city' in w.tags and 'name' in w.tags:

            housenumber_match = False

            street_match = self.searching_name_street.lower() == w.tags['addr:street'].lower()
            city_match = self.searching_name_city.lower() == w.tags['addr:city'].lower()
            name_match = self.searching_name_name.lower() in w.tags['name'].lower().split()
            if 'addr:housenumber' in w.tags:
                housenumber_match = self.searching_name_housenumber.lower() == w.tags['addr:housenumber'].lower()

            if name_match and city_match and street_match:
                if housenumber_match:
                    print('A way match. Nodes references stored.')
                    self.nodes_id = np.zeros(len(w.nodes))
                    for ref_num in range(0, len(w.nodes)):
                        self.nodes_id[ref_num] = w.nodes[ref_num].ref
                    # TODO: find a way to stop the searching class and jump out
                else:
                    print('The way housenumber does not match. Nodes references stored anyway.')
                    self.nodes_id = np.zeros(len(w.nodes))
                    for ref_num in range(0, len(w.nodes)):
                        self.nodes_id[ref_num] = w.nodes[ref_num].ref
                    # TODO: find a way to stop the searching class and jump out

            self.count += 1
            if self.count % 10000 == 0:
                print(f'{self.count} ways processed.')


def get_multi_ways_coordinates(waylist, filepath):

    ACMW = AddressToCoordinatesMultiWaysHandler(waylist)

    reader = osmium.io.Reader(filepath)
    # CalssShouldProceed = True

    # for num_tmp in range(0, len(waylist)):
    #     if ACMW.nodes_id[num_tmp][0] == 0:
    #         print('Search not ended.')
    #         CalssShouldProceed = True
    #         osmium.apply(reader, ACMW)
    #     else:
    #         CalssShouldProceed = False
    #
    # # if CalssShouldProceed:
    # osmium.apply(reader, ACMW)
    if not ACMW.finish:
        # osmium.apply(reader, ACMW)
        ACMW.apply_file(filepath)
    print('aaa')


    return ACMW.nodes_id


class MultiNodeSearchingFromWayList(osmium.SimpleHandler):
    def __init__(self, nodes_id_list):
        osmium.SimpleHandler.__init__(self)
        self.nodes_id_list = nodes_id_list

        # create a save list for every way
        for i in range(0, len(nodes_id_list)):
            # TODO: rewrite
            exec("self.way_lon_%s = {}"%i)
            exec("self.way_lat_%s = {}"%i)

        self.node_position_list = np.zeros([len(nodes_id_list), 80])
        self.count = 0

    def node(self, n):

        # count the nodes already processed
        self.count += 1
        if self.count % 1000000 == 0:
            print(f'{self.count} nodes processed.')

        for way_num in range(0, len(self.nodes_id_list)):
            for node_num in range(0, len(self.nodes_id_list[way_num])):
                if n.id == self.nodes_id_list[way_num][node_num]:
                    pass
                    # TODO: rewrite these number-giving sentences
                    # exec("self.way_lon_%s[%s] = %f" %(way_num node_num n.location.lon))
                    # exec("self.way_lon_%s[%s] = %f" % (way_num node_num n.location.lon))
                    #
                    # self.node_position.append((n.id, n.location.lon, n.location.lat))



class AddressToCoordinatesMultiWaysHandler(osmium.SimpleHandler):

    def __init__(self, waylist):
        osmium.SimpleHandler.__init__(self)
        self.count = 0
        self.nodes_id = []
        self.finish = False

        # init
        self.searching_name_city = [0]*len(waylist)
        self.searching_name_street = [0]*len(waylist)
        self.searching_name_housenumber = [0]*len(waylist)
        self.searching_name_name = [0]*len(waylist)

        # manually set the maximal way nodes as 80, if any way has more than 80 nodes, it would raise error.
        self.nodes_id = np.zeros([len(waylist), 80])

        # waylist should follow the format: waylist[number] = [name, housenumber, street, city]
        for num in range(0, len(waylist)):
            self.searching_name_city[num] = waylist[num][3]
            self.searching_name_street[num] = waylist[num][2]
            self.searching_name_housenumber[num] = waylist[num][1]
            self.searching_name_name[num] = waylist[num][0]

    def way(self, w):
        if 'addr:street' in w.tags and 'addr:city' in w.tags and 'name' in w.tags:

            # shows how much ways are processed
            self.count += 1
            if self.count % 10000 == 0:
                print(f'{self.count} ways processed.')

            for way_num in range(0, len(self.searching_name_name)):
                if self.searching_name_street[way_num].lower() == w.tags['addr:street'].lower():
                    if self.searching_name_city[way_num].lower() == w.tags['addr:city'].lower():
                        if self.searching_name_name[way_num].lower() in w.tags['name'].lower().split()\
                                or w.tags['name'].lower() == self.searching_name_name[way_num].lower():

                            # write the nodes coordinates into another saving variable
                            for ref_num in range(0, len(w.nodes)):
                                self.nodes_id[way_num, ref_num] = w.nodes[ref_num].ref

                            # print shows weather the name matches
                            if 'addr:housenumber' in w.tags\
                                    and self.searching_name_housenumber[way_num].lower() == \
                                    w.tags['addr:housenumber'].lower():
                                print('A way match. Nodes references stored.')
                            else:
                                print('The way housenumber does not match. Nodes references stored anyway.')

                            # delete this node information to avoid further search match
                            self.searching_name_street[way_num] = ''
                            self.searching_name_city[way_num] = ''

                            # check if all the ways in waylist have been found. if yes, leave the class
                            if all(self.nodes_id[:, 1] != 0):
                                self.finish = True
                                # TODO: find a way to stop the osmium class when the searching process finish and jump out
                                reader.close(self)
                                # self.handler.stop()
                            break
                        else:
                            continue
                    else:
                        continue
                else:
                    continue

                """The following code is the old version, but it also runs under such condition."""

            #     street_match = self.searching_name_street[way_num].lower() == w.tags['addr:street'].lower()
            #     city_match = self.searching_name_city[way_num].lower() == w.tags['addr:city'].lower()
            #     name_match = self.searching_name_name[way_num].lower() in w.tags['name'].lower().split()
            #     if street_match and city_match and name_match:
            #         temp_waynum = way_num
            #         break
            #     else:
            #         if way_num == len(self.searching_name_name)-1:
            #             print('The node does not match any way in the list.')
            #             return
            #         continue
            #
            # if 'addr:housenumber' in w.tags:
            #     housenumber_match = self.searching_name_housenumber.lower() == w.tags['addr:housenumber'].lower()
            #
            # if name_match and city_match and street_match:
            #     if housenumber_match:
            #         print('A way match. Nodes references stored.')
            #
            #         for ref_num in range(0, len(w.nodes)):
            #             self.nodes_id[temp_waynum, ref_num] = w.nodes[ref_num].ref
            #     else:
            #         print('The way housenumber does not match. Nodes references stored anyway.')
            #         for ref_num in range(0, len(w.nodes)):
            #             self.nodes_id[temp_waynum, ref_num] = w.nodes[ref_num].ref


def get_one_node_coordinates(city, street, housenumber, name, filepath):
    ACN = AddressToCoordinatesNodeHandler(city, street, housenumber, name)
    ACN.apply_file(filepath)
    return ACN.address


class AddressToCoordinatesNodeHandler(osmium.SimpleHandler):

    def __init__(self, keyword_city, keyword_street, keyword_housenumber, keyword_name):
        osmium.SimpleHandler.__init__(self)
        self.address = None
        self.count = 0

        self.searching_name_city = keyword_city
        self.searching_name_street = keyword_street
        self.searching_name_housenumber = keyword_housenumber
        self.searching_name_name = keyword_name

    def node(self, n):
        if 'addr:street' in n.tags and 'addr:housenumber' in n.tags and 'addr:city' in n.tags and 'name' in n.tags:

            # other elements should be matched, while the name should just in the node tag
            street_match = self.searching_name_street.lower() == n.tags['addr:street'].lower()
            housenumber_match = self.searching_name_housenumber.lower() == n.tags['addr:housenumber'].lower()
            city_match = self.searching_name_city.lower() == n.tags['addr:city'].lower()
            name_match = self.searching_name_name.lower() in n.tags['name'].lower().split()

            if street_match and housenumber_match and city_match:
                if name_match:
                    print('A node match. Geo coordinates stored.')
                    self.address = (n.tags['addr:street'], n.tags['addr:housenumber'], n.location.lon, n.location.lat)
                    # self.handler.stop()
                    return
                    # TODO: fix the problem that the class cannot be jumped out
                else:
                    # The name does not match, while city, street and housenumber match;
                    print('The node name does not match, but geo coordinates are stored anyway.')
                    self.address = (n.tags['addr:street'], n.tags['addr:housenumber'], n.location.lon, n.location.lat)
                    # self.handler.stop()
                    return
                    # TODO: fix the problem that the class cannot be jumped out

            self.count += 1
            if self.count % 1000000 == 0:
                print(f'{self.count} nodes processed.')

    def after_nodes(self):
        if self.address is None:
            print('Node not found.')


class AddressToCoordinatesRelationHandler(osmium.SimpleHandler):

    def __init__(self, keyword_city, keyword_street, keyword_housenumber, keyword_name):
        osmium.SimpleHandler.__init__(self)
        self.relation = None

        self.searching_name_city = keyword_city
        self.searching_name_street = keyword_street
        self.searching_name_housenumber = keyword_housenumber
        self.searching_name_name = keyword_name

    def relation(self, r):
        if 'addr:city' in r.tags and 'name' in r.tags:

            street_match = False

            if 'addr:street' in r.tags:
                street_match = self.searching_name_street.lower() == r.tags['addr:street'].lower()
            city_match = self.searching_name_city.lower() == r.tags['addr:city'].lower()
            name_match = self.searching_name_name.lower() in r.tags['name'].lower().split()

            if name_match and city_match:
                if street_match:
                    print('Relation found. Inside ways stored.')
                    self.relation = r
                else:
                    # The street does not match, while city and name match;
                    print('The street does not match, but the ways inside are stored anyway.')
                    self.relation = r


class FindNodeWithRef(osmium.SimpleHandler):

    def __init__(self, ref_num):
        osmium.SimpleHandler.__init__(self)
        self.ref_num = ref_num
        self.node_coordinates = []

    def node(self, n):
        if n.id == self.ref_num:
            self.node_coordinates.append((n.id, n.location.lon, n.location.lat))


def get_coordinates(ref, bbox):
    # TODO: finish the funktion
    pass
