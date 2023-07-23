from IO.excel_input import load_excel


def get_test_area_retail_inflation_correction(test_area_retail, year, standard_year,
                                              inflation_xlsx_file="C:/Users/86781/PycharmProjects/pythonProject/data/Inflationsrate.xlsx",
                                              inflation_xlsx_sheet="inflation"):
    """Use the input whole test area retail amount, inflation rate of years and retail-business trade proportion
    file to converse the retail amount into standard retail amount for the test area.
    :param float test_area_retail: The uncorrected test area business trade amount,
    :param int year: the to-be-predicted year,
    :param int standard_year: the year that has cargo weight-price relationship available,
    :param str inflation_xlsx_file: file path and name of the .xlsx file containing inflation data over the period,
    :param str inflation_xlsx_sheet: the corresponding file's sheet name,
    :return: the corrected test area's retail amount, standard with year ....
    """

    # check the input
    if isinstance(test_area_retail, float) or isinstance(test_area_retail, int):
        pass
    else:
        print('Retail data of test area error. Please check your input.')
        return 0

    if isinstance(year, int) and isinstance(standard_year, int):
        pass
    else:
        print('Year format error. Please check your input.')
        return 0

    # load the data from .xlsx files, here the sheet name should be the same as those in the .xlsx files
    inflation = load_excel(inflation_xlsx_file, inflation_xlsx_sheet)

    # set a function to deal with the percentages in inflation .xlsx file and transform those into decimal
    def parseFloat(str):
        try:
            return float(str)
        except:
            str = str.strip()
            # if is percentage
            if str.endswith("%"):
                return float(str.strip("%").strip()) / 100
            raise Exception("Cannot parse %s" % str)

    if (2000 <= year <= 2025) and (2000 <= standard_year <= 2025):
        pass
    else:
        print('Year beyond limitation. Please check and retry.')

    inflation_decimal = []

    # change percentage into decimal number
    for num_temp in range(1, len(inflation)):
        inflation_decimal.append(parseFloat(inflation.values[num_temp][1]))

    # set value for inflation rate from 2023-2025 as the average rate from the past 15 years(2008-2022)
    # note: the inflation rate can change rapidly, so an average estimate can have big error over a long period.
    # here only 3 years from 2023 to 2025
    temp = 0
    for year_temp_3years in range(16, 31):
        temp += inflation_decimal[year_temp_3years]
    inflation_decimal.append(temp / 15)  # year 2023
    inflation_decimal.append(temp / 15)  # year 2024
    inflation_decimal.append(temp / 15)  # year 2025

    # the inflation rate from standard year to to-be-predicted year
    pdt = 1
    price = 0
    if year >= standard_year:
        for year_temp in range(standard_year - 1992, year - 1992):
            pdt *= (inflation_decimal[year_temp] + 1)
        price = test_area_retail / pdt
    else:
        for year_temp in range(year - 1992, standard_year - 1992):
            pdt *= (inflation_decimal[year_temp] + 1)
        price = test_area_retail * pdt

    return price

# # test code
# a = get_test_area_retail_inflation_correction(100.0, 2023, 2018)
# pass
