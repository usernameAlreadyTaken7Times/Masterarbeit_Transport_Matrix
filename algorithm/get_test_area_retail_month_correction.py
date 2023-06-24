import pandas as pd
from scipy.optimize import curve_fit

from IO.excel_input import load_excel


def get_state_num_from_state_name(state_name):
    # use the input state name to find a corresponding state index
    name = state_name
    state_num = -1

    # check if the input name is a string
    if not isinstance(name, str):
        print("Input type error. please use string instead.")
        return -1
    else:
        if name.lower() == "baden-württemberg" or name.lower() == "baden-wuerttemberg":
            state_num = 1
        elif name.lower() == "bayern":
            state_num = 2
        elif name.lower() == "berlin":
            state_num = 3
        elif name.lower() == "brandenburg":
            state_num = 4
        elif name.lower() == "bremen":
            state_num = 5
        elif name.lower() == "hamburg":
            state_num = 6
        elif name.lower() == "hessen":
            state_num = 7
        elif name.lower() == "mecklenburg-vorpommern":
            state_num = 8
        elif name.lower() == "niedersachsen":
            state_num = 9
        elif name.lower() == "nordrhein-westfalen":
            state_num = 10
        elif name.lower() == "rheinland-pfalz":
            state_num = 11
        elif name.lower() == "saarland":
            state_num = 12
        elif name.lower() == "sachsen":
            state_num = 13
        elif name.lower() == "sachsen-anhalt":
            state_num = 14
        elif name.lower() == "schleswig-holstein":
            state_num = 15
        elif name.lower() == "thüringen" or name.lower() == "thueringen":
            state_num = 16
        else:
            print("state name not match. please check your input.")
            state_num = -1

    return state_num


def get_test_area_retail_month_correction(test_area_retail, month, state,
                                          monatsanteil_xlsx_file="C:/Users/86781/PycharmProjects/pythonProject/data/Monatanteil.xlsx"):
    """Use the input test area retail amount, month and the corresponding german state to calculate the sale amount of
    the given month.
    :param float test_area_retail: The uncorrected test area business trade amount,
    :param int month: the to-be-predicted month,
    :param string state: the name of german state, in which the test area is located,
    :param str monatsanteil_xlsx_file: file path and name of the .xlsx file containing month percentage data of the
    chosen state,
    :return: the corrected test area's monthly retail amount.
    """

    # check the input
    if isinstance(test_area_retail, float) or isinstance(test_area_retail, int):
        pass
    else:
        print('Retail data of test area format error. Please check your input.')
        return 0

    if isinstance(month, int):
        pass
    else:
        print('Input month format error. Please check and retry.')
        return 0



    # load the data from .xlsx files, here the sheet name should be the same as those in the .xlsx files
    anteil = load_excel(monatsanteil_xlsx_file, "monat_anteil")

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

    if 12 >= month >= 1:
        pass
    else:
        print('Month beyond limitation. Please check and retry.')







# test code
a = get_test_area_retail_month_correction(100, 2024)
pass
