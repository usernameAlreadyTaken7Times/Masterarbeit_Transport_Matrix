from algorithm.calc_test_area_idx_info import get_index_in_csv
from algorithm.calc_test_area_idx_info import get_block_pop
from algorithm.calc_test_area_idx_info import get_area_blocks_idx
from algorithm.calc_test_area_idx_info import get_test_area_info
from algorithm.get_test_area_pop import get_test_area_pop_whole
from alternative_Nominatim.get_shop_list_Nominatim import get_shop_list_Nominatim

from algorithm.get_test_area_retail import get_test_area_retail

# pop = get_block_pop(1, 2021)
# print(pop)

# get_index_in_csv(9.9046415, 53.457823, 10.2529317, 53.6522254)
# get_area_blocks_idx(9.9046415, 53.457823, 10.2529317, 53.6522254)
# a = get_area_blocks_idx(9.9046415, 53.457823, 9.9120015, 53.4650054, 2)

# a = get_test_area_info(9.9046415, 53.457823, 9.9120015, 53.4650054, 2023)
# b = get_test_area_pop_whole(9.9046415, 53.457823, 9.9120015, 53.4650054, 2023)


# Nominatim_find_shops(10.5091, 52.2599, 10.5250, 52.2690)
# get_shop_list_Nominatim(10.46843,52.27246,10.53718,52.25082)


retail = get_test_area_retail(2023, "Niedersachsen", 10.46843, 52.25082, 10.53718, 52.27246)

pass
