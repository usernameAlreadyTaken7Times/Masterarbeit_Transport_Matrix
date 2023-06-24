import numpy as np
import pandas
import os
from scipy.optimize import curve_fit


def get_block_pop(idx, year, data_path='C:/Users/86781/PycharmProjects/pythonProject/data/'):
    """Use the regression analyzing to predict the population in the chosen block in certain year.
    If the year is in the period of 2000-2020, use historical data;
    if the year is in the period of 2020-2025, use predication data; (regression method)
    if the year is more than 2025, an error occurs,
    because population predication is not precise for long periods.

    :param int idx: The index(row) of the block in the .csv file,
    :param int year: the year you want to predict, year should not be bigger than 2025, or an error occurs,
    :param str data_path: the data path, in which the .csv file is stored,
    :return: the predicted population number in the chosen block, in certain year.
    """
    # For every block in the test area, read the historical data from .csv file and fit with a suitable function.
    filename = 'pop_dsy_merged.csv'

    # use mode to distinguish population calculation method:
    # for 2000-2020 use historical data; (mode = 0)
    # for 2021-2025 use regression method to predict; (mode = 1)
    # otherwise raise error.
    mode = -1  # mode init as -1

    # check if the file exists or not
    if os.path.exists(data_path + filename):
        pass
    else:
        print('No population density file found. Please run the update program for world population density files.')

    # check if the input year in the chosen periods and set mode
    if isinstance(year, int):
        pass
    else:
        print('Input year format error. Please check your input year and then retry.')
        return 0

    if 2000 <= year <= 2020:
        print(f'Input year is {str(year)}, using historical data from .csv file.')
        mode = 0
    elif 2020 < year <= 2025:
        print(f'Input year is {str(year)}, using predication data from .csv file.')
        mode = 1
    else:
        print('Your input year is beyond limitation. Please check your input year and then retry.')
        return 0

    # read the file and store arrays init
    pop_csv = pandas.read_csv(data_path + filename)
    pop_block = np.zeros(21)
    year_block = np.zeros(21)

    # get population data and year data from csv file
    for year_temp in range(2000, 2021):
        pop_block[year_temp - 2000] = pop_csv.values[idx][year_temp - 1998]
        year_block[year_temp - 2000] = year_temp

    # Some blocks have very fluctuating population number over time. This can be because policy changes or city
    # construction, which is hard to predict over long time periods without other literature and method support.
    # However, for a certain block, the population on it does show a pattern because of its own infrastructure,
    # industry model and geographical conditions. So a regression analyzing is still useful, when the year is not
    # too far away. Here only when the input year is not bigger than 2026, a regression method is applied.

    # for mode = 1, use regression method to predict population
    if mode == 1:
        def func1(x, k, b):
            return k * x + b

        popt1, pcov1 = curve_fit(func1, year_block, pop_block)
        return popt1[0] * year + popt1[1]

    # for mode = 0, use historical data directly
    elif mode == 0:
        return pop_block[year - 2000]

    # should not go this far, just for insurance
    elif mode == -1:
        print('Internal function error. Please check this script.')
        return 0

# # test code
# abc = get_block_pop(20, 2024)
# pass