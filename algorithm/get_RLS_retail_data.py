import os

from IO.excel_input import load_excel


def get_RLS_retail_data(year, file, sheet):
    """This function aims to get the good value-good weight relationship of the chosen year, unit Euro/kg
    :param int year: the year whose data you want to use, and it should be in the range of 2011-2020.
    """

    # the input testing phrase is skipped. I just assume the inputs are valid
    if os.path.exists(file):
        pass
    else:
        print("RLS file not availavle. Please check and retry.")
        raise FileNotFoundError

    # read data
    RLS = load_excel(file, sheet)

    relation = RLS.values[year - 2011][4] / RLS.values[year - 2011][3] * 1000

    return relation

# # test data
# aa = [get_RLS_retail_data(i,
#                   "C:/Users/86781/PycharmProjects/pythonProject/data/RLS.xlsx", "RLS") for i in range(2011, 2020)]
# pass
