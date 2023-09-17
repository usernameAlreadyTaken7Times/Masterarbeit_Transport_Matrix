import osmnx as ox
import networkx as nx
from multiprocessing import Process, cpu_count, Pool, Manager
from settings.program_conf import *


# the calculating core for distance database generating
class cal():
    def __init__(self):
        self.manager = Manager
        self.dis_list = self.manager().list()

    # build a function for route distance calculating in process pool
    def distance_cal(self, G, Arg, num):
        # argument in the order of G, lon1, lat1, lon2, lat2, id_num

        # append the input coordinates to the nodes in .osm file
        orig = ox.nearest_nodes(G, X=Arg[0], Y=Arg[1])
        dest = ox.nearest_nodes(G, X=Arg[2], Y=Arg[3])

        dis = nx.shortest_path_length(G, orig, dest, weight='length')  # unit in meter
        print(f'{num}. data finishes.')
        self.dis_list.append(dis)
        return dis

    def flow(self, G, Arg, cpu_num, loop_num):
        pool = Pool(cpu_num)
        for i in range(loop_num):
            pool.apply_async(self.distance_cal, args=(G, Arg[i], i))
        pool.close()
        pool.join()


cal1 = cal()
cal1.flow(G=G, Arg=list_coord, cpu_num=cpu_num, loop_num=len(list_coord))
dis = cal1.dis_list

# delete G to save memery
del G



