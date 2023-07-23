from algorithm.calc_test_area_idx_info import get_test_area_info


def get_test_area_pop_whole(lon1, lat1, lon2, lat2, year):
    """Return the whole population amount of test area 0 and test area 1 in the given year for the chosen state.
    Please note: this function calls for the calc_test_area function again, so for efficiency, it should be used
    in test only.
    :param float lon1: The minimum longitude of the points,
    :param float lat1: the minimum latitude of the points,
    :param float lon2: the maximum longitude of the points,
    :param float lat2: the maximum latitude of the points,
    :param int year: the year of the to-predict area,
    :return: the population of area 0 and area 1, unit of measurement people.
    :rtype: Float
    """

    temp_area_info = get_test_area_info(lon1, lat1, lon2, lat2, year)

    return sum(temp_area_info[5]) + sum(temp_area_info[11])

