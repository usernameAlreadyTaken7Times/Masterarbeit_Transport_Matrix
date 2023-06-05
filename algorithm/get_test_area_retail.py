from algorithm.calc_state_retail_average import get_retail_average
from algorithm.get_test_area_pop import get_test_area_pop_whole

def get_test_area_retail(year, state, lon1, lat1, lon2, lat2):
    """Get the test area's whole retail amount for the given state and year.
    :param int year: Year,
    :param str state: german state,
    :param float lon1: minimum longitude of the test area shop list,
    :param float lat1: minimum latitude of the test area shop list,
    :param float lon2: maximum longitude of the test area shop list,
    :param float lat2: maximum latitude of the test area shop list,
    :return: the test area retail amount in the given year and state.
    """

    retail_avg = get_retail_average(year, state)
    pop = get_test_area_pop_whole(lon1, lat1, lon2, lat2, year)

    return retail_avg * pop
