import pandas as pd
from scipy.optimize import curve_fit

from IO.excel_input import load_excel


def get_test_area_retail_markanteil_correction(test_area_retail, year,
                                              markanteil_xlsx_file="C:/Users/86781/PycharmProjects/pythonProject/data/Inflationsrate.xlsx"):
    """Use the input for whole germany big business concerns' sale amount / whole retail sale amount
    file to converse the retail amount into standard retail amount for the test area.
    :param float test_area_retail: The uncorrected test area business trade amount,
    :param int year: the to-be-predicted year,
    :param str markanteil_xlsx_file: file path and name of the .xlsx file containing inflation data over the period,
    :return: the corrected test area's retail amount, standard with year ....
    """

    # check the input
    if isinstance(test_area_retail, float) or isinstance(test_area_retail, int):
        pass
    else:
        print('Retail data of test area format error. Please check your input.')
        return 0

    if isinstance(year, int):
        pass
    else:
        print('Input year format error. Please check and retry.')
        return 0

    # load the data from .xlsx files, here the sheet name should be the same as those in the .xlsx files
    anteil = load_excel(markanteil_xlsx_file, "shop_anteil")

    # set a function to deal with the percentages in antiel .xlsx file and transform those into decimal
    def parseFloat(str):
        try:
            return float(str)
        except:
            str = str.strip()
            # if is percentage
            if str.endswith("%"):
                return float(str.strip("%").strip()) / 100
            raise Exception("Cannot parse %s" % str)

    if 2025 >= year >= 2000:
        pass
    else:
        print('Year beyond limitation. Please check and retry.')
        return 0

    anteil_decimal = []
    year_decimal = []

    # change percentage into decimal number
    for num_temp in range(1, len(anteil)):
        anteil_decimal.append(parseFloat(anteil.values[num_temp][1]))
        year_decimal.append(anteil.values[num_temp][0])

    # use a linear regression to get anteil value for year 2022-2025
    def func(x, b, k):
        return x * b + k

    popt, pcov = curve_fit(func, year_decimal, anteil_decimal)

    # if you can escape a loop, why make any trouble :-)
    anteil_decimal.append(popt[0] * 2022 + popt[1])  # year 2022
    anteil_decimal.append(popt[0] * 2023 + popt[1])  # year 2023
    anteil_decimal.append(popt[0] * 2024 + popt[1])  # year 2024
    anteil_decimal.append(popt[0] * 2025 + popt[1])  # year 2025

    # well, not completely escaping
    price = 0
    for year_temp in range(2000, 2026):
        if int(year_temp) == year:
            price = test_area_retail * anteil_decimal[year_temp - 2000]

    return price

# # test code
# a = get_test_area_retail_markanteil_correction(100, 2024)
# pass
