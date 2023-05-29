import numpy as np
import pandas
import os
from scipy.optimize import curve_fit


def get_block_pop(idx, year, data_path='C:/Users/86781/PycharmProjects/pythonProject/data/'):
    """Use the regression analyzing to predict the population in the chosen block in certain year.
    :param int idx: The index(row) of the block in the .csv file,
    :param int year: the year you want to predict,
    :param str data_path: the data path, in which the .csv file is stored,
    :return: the predicted population number in the chosen block, in certain year.
    """
    # For every block in the test area, read the historical data from .csv file and fit with a suitable function.
    filename = 'pop_dsy_merged.csv'

    # check if the file exists or not
    if os.path.exists(data_path + filename):
        pass
    else:
        print('No population density file found. Please run the update program for world population density files.')

    pop_csv = pandas.read_csv(data_path + filename)
    pop_block = np.zeros(21)
    year_block = np.zeros(21)

    for year_temp in range(2000, 2021):
        pop_block[year_temp - 2000] = pop_csv.values[idx][year_temp - 1998]
        year_block[year_temp - 2000] = year_temp

    # Some blocks have very fluctuating population number over time. This can be because policy changes or city
    # construction, which is hard to predict over long time periods. Here the fluctuation rate is set to 20% of
    # the average population number. If the change is more than that value, use another predict algorithm.

    # diff: the difference of max and min data of population
    diff = max(pop_block.max() - pop_block.mean(), pop_block.mean() - pop_block.min())

    def func1(x, k, b):
        return k * x + b

    popt1, pcov1 = curve_fit(func1, year_block, pop_block)

    # max_..., min_...: the max and min data of the fitting graph
    max_pop_data_block = max(popt1[0] * 2000 + popt1[1], popt1[0] * 2020 + popt1[1])
    min_pop_data_block = min(popt1[0] * 2000 + popt1[1], popt1[0] * 2020 + popt1[1])

    if abs(diff - (max_pop_data_block - min_pop_data_block)) / pop_block.mean() <= 0.20:
        # if the fluctuation rate is less than 20%, use regression algorithm directly
        return popt1[0] * year + popt1[1]
    else:
        # if the fluctuation rate is more than 20%, use another algorithm
        # TODO: try to find a better fitting method, now the regression method is still being used
        return popt1[0] * year + popt1[1]
