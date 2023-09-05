import time
import multiprocessing as mp


class OP():
    def __init__(self):
        # 直接调用 Manager 提供的 list() 和 dict()
        self.manager = mp.Manager
        self.mp_lst = self.manager().list()
        self.length = 64

    def proc_func(self, i, j):
        self.mp_lst.append(i)
        time.sleep(0.1)

    def flow(self, a):
        pool = mp.Pool(16)
        for i in range(self.length):
            pool.apply_async(self.proc_func, args=(i+a, i*2))
        pool.close()
        pool.join()


if __name__ == '__main__':

    start_time = time.time()
    op = OP()
    op.flow(3)
    print(op.mp_lst)
    print(time.time() - start_time)