import numpy as np
import pandas as pd
from openpyxl import load_workbook
from scipy import interpolate
from scipy.optimize import curve_fit

from IO.excel_input import load_excel


def BIP_handel_pre_process(Umsatz_file='C:/Users/86781/PycharmProjects/pythonProject/data/BIP_handel_Umsatz.xlsx',
                           BIP_file='C:/Users/86781/PycharmProjects/pythonProject/data/BIP und Einkommen.xlsx'):
    """This function aims to use interpolation method to fill the blanks in BIP_handel data for further use.
    However, since the spline curve is not good at data prediction, the BIP_handel data should be guaranteed within
    a certain time range. So in this script, only the blanked data of BIP_handel from year 2015 to 2022 will be
    generated.
    Noted: This function should be called before calculating the average BIP_handel in script
    `algorithm.calc_state_retail_average`.
    :param str Umsatz_file: The .xlsx file containing the BIP_Umsatz data,
    :param str BIP_file: the .xlsx file containing the BIP_handel data,
    :rtype: None
    """

    Umsatz = load_excel(Umsatz_file, "Umsatz")

    # copy the data into a new para for the further process
    for i in range(1, 17):

        # temp para init
        year_temp = []
        Umsatz_temp = []
        year_nan = []
        Umsatz_nan = []
        for j in range(11, 20):

            # read all non-null cells' data
            if str(Umsatz.values[j][i]) != 'nan':
                year_temp.append(Umsatz.values[j][0])
                Umsatz_temp.append(Umsatz.values[j][i])

                # to avoid writing problems, avoid any decimal number in the .xlsx file
                Umsatz.values[j][i] = round(Umsatz.values[j][i])
            else:
                year_nan.append(Umsatz.values[j][0])

        if len(year_nan) <= 4:
            # interpolation and force it to go through all datapoints
            func = interpolate.UnivariateSpline(year_temp, Umsatz_temp, s=0)
            Umsatz_nan = func(year_nan)
        else:
            # for state data which much data is missing, use linear interpolation with warning
            print('Data is not adequate. Use linear interpolation. There may be large errors.')

            def func(x, k, b):
                return k * x + b

            popt, pcov = curve_fit(func, year_temp, Umsatz_temp)
            # use regression to fit data
            for year_nan_num in range(len(year_nan)):
                Umsatz_nan.append(popt[0] * year_nan[year_nan_num] + popt[1])

        # write the interpolation data back to Umsatz
        for j1 in range(len(year_nan)):

            # to avoid writing problems, avoid any decimal number in the .xlsx file
            Umsatz.values[year_nan[j1]-2003][i] = round(Umsatz_nan[j1])

    # write the data into BIP_handel_und Einkommen .xlsx file data
    with pd.ExcelWriter(BIP_file, engine='openpyxl', mode='a') as writer:
        if 'BIPhandel' in writer.sheets.keys():
            print('Worksheet already in worksheet. Please delete the sheet named <BIPhandel> manually.')
            return 0
        # writer.book = load_workbook(BIP_file)
        # writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
        Umsatz.to_excel(writer, sheet_name='BIPhandel', index=False)
    return 0

    # Umsatz.to_excel(BIP_file, sheet_name='BIPhandel')

# # test code
# BIP_handel_pre_process()
# pass
