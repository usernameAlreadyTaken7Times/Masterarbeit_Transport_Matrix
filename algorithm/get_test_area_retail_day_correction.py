
def get_test_area_retail_day_correction(sale_amount, month, year):
    """This function aims to convert the monthly sale amount (in Euro) of shops to the daily sale amount (also in Euro).
    :param list sale_amount: The sale number of shops in the given area,
    :param int month: the simulated month,
    :param int year: the simulated year.
    """

    # test the year is a leap year or not,
    # in the test area's period,
    # all years that can be evenly divided by 4 are leap years, we do not need to consider the situation like 1900

    leap_year = False
    day = 30

    if year % 4 == 0:
        leap_year = True

    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        day = 31
    elif month == 2:
        if leap_year:
            day = 29
        else:
            day = 28

    sale_amount_day = []
    for shop_num in range(len(sale_amount)):
        sale_amount_day.append(sale_amount[shop_num] / day)

    return sale_amount_day
