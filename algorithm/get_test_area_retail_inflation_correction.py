import pandas as pd

from IO.excel_input import load_excel


def get_test_area_retail_inflation_coorection(test_area_retail, year, inflation_xlsx_file, retail_Proportion_xlsx_file):
    """Use the input whole test area retail amount, inflation rate of years and retail-business trade proportion
    file to converse the retail amount into standard retail amount for the test area.
    :param float test_area_retail: The uncorrected test area business trade amount,
    :param int year: the to-be-predicted year,
    :param str inflation_xlsx_file: file path and name of the .xlsx file containing inflation data over the period,
    :param str retail_Proportion_xlsx_file: file path and name of the .xlsx file containing retail-business trade
     proportion data,
    :return: the corrected test area's retail amount, standard .....
    """

    # check the input
    if isinstance(test_area_retail, float):
        pass
    else:
        print('Retail data of test area error. Please check your input.')
        return 0

    inflation = load_excel(inflation_xlsx_file)
    pro = load_excel(retail_Proportion_xlsx_file)

    # use regression analyze to get the to-be-predicted year's data




