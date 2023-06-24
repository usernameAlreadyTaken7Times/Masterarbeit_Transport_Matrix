import pyproj
#
#
# def convert_to_plane_rectangular(lat, lon):
#     proj = pyproj.Proj(proj='utm', zone=10, ellps='WGS84')
#     x, y = proj(lon, lat)
#     return x, y
#
# lat = 50
# lon = 0
# lat1 = 50.0001
# lon1 = 180
# x, y = convert_to_plane_rectangular(lat, lon)
# x1, y1 = convert_to_plane_rectangular(lat1, lon1)
# print(f"Diff_X: {abs(x - x1)}, Diff_Y: {abs(y - y1)}")


import re

def extract_shop_details(address):
    """This function is used to separate the name, housenumber and street of a shop from its address string.
     Please note: sometimes in the Nominatim server's result, the name or the housenumber is not available. But it is
      assumed that they will not be absent at the same time.
      :param str address: The string of the shop address, containing housenumber, shop name and street at the same time.
      """
    if isinstance(address, str):
        pass
    else:
        print('Check your input address string.')
    slt = address.split(', ')

    # postcode index
    post_idx = -1
    for num_temp in range(len(slt)-3, len(slt)):
        if slt[num_temp].isdigit() and len(slt[num_temp]) == 5:
            post_idx = num_temp

    # housenumber index
    number_idx = -1
    number = None
    for num_temp1 in range(0, post_idx-2):
        # some housenumber have one character at the end, like '15a', ''30c'
        if slt[num_temp1].isdigit() or slt[num_temp1][0:-1].isdigit():
            number_idx = num_temp1
            number = slt[num_temp1]
        # in this case, no housenumber is available
        else:
            pass

    # name index
    name_idx = -1
    name = None

    # when the house number is not available or at 2. place, assume the name is available at slt[0]
    if number_idx == -1 or number_idx == 1:
        name = slt[0]
        name_idx = 0
    # if housenumber is at 1. place, name is not available
    elif number_idx == 0:
        pass
    elif number_idx >= 2:
        # TODO: before housenumber there are two spots
        pass

    # street string
    street = None

    # no housenumber available, street is the next spot of name (There exists at least one of name and housenumber)
    if number_idx == -1:
        if name_idx == 0:
            street = slt[name_idx+1]
        # both name and housenumber is not there(backup)
        else:
            street = slt[0]
    # no name, 1. place:housenumber, 2. place:street
    elif number_idx == 0:
        street = slt[1]
    # name takes more than one place
    else:
        street = slt[number_idx+1]

    return name, number, street




