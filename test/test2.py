from xml.dom.minidom import parse
import xml.dom.minidom
def check_pure_node(nodes, lon, lat, tlr, street, housenumber, name):
    """Use the whole node set to check weather any of these nodes meets the standard of the given shop.
    :param nodes: The document node elements from osm xml file,
    :param float lon: the longitude of the shop,
    :param float lat: the latitude of the shop,
    :param float tlr: the tolerance of the shop's coordinates,
    :param str street: the given shop's street,
    :param str housenumber: the given shop's house number,
    :param str name: the given shop's name,
    :return: if any node is the given shop and the node itself for further assessment.
    """

    # para init
    shop_match = False
    node_temp = None

    for node in nodes:

        # indicator init
        street_match = False
        housenumber_match = False
        name_match = False
        lon_match = False
        lat_match = False

        geo_match = False

        # If the input housenumber, street or name array is empty for a specific shop
        # (not available from Nominatim), then set it as matched by default.
        if housenumber is None:
            housenumber_match = True
        if street is None:
            street_match = True
        if name is None:
            name_match = True

        # check the geo_coordinates of the node
        lon_match = lon - tlr / 2 <= float(node.getAttribute("lon")) <= lon + tlr / 2
        lat_match = lat - tlr / 3 <= float(node.getAttribute("lat")) <= lat + tlr / 3
        geo_match = lon_match and lat_match

        if geo_match:
            if node.getElementsByTagName("tag"):
                for nd_num in range(len(node.getElementsByTagName("tag"))):

                    # street match
                    if street is not None:
                        if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'addr:street':
                            if node.getElementsByTagName("tag")[nd_num].getAttribute("v").lower() == street.lower():
                                street_match = True

                    # housenumber match
                    if housenumber is not None:
                        if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'addr:housenumber':
                            if node.getElementsByTagName("tag")[nd_num].getAttribute(
                                    "v").lower() == housenumber.lower():
                                housenumber_match = True

                    # Name match for both 'name' and 'brand.'
                    # Here, a small text recognition program is involved to split the full shop's name by .osm
                    # file.
                    # It will loop through all name phrases and try to find a match with the input shop name.
                    # The same for the following brand searching process.
                    if name is not None:
                        if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'name':
                            for tag_name_split in node.getElementsByTagName("tag")[nd_num].getAttribute(
                                    "v").lower().split():
                                for shop_name_split in name.lower().split():
                                    if tag_name_split == shop_name_split:
                                        name_match = True
                                        break

                        if node.getElementsByTagName("tag")[nd_num].getAttribute("k") == 'brand':
                            for tag_brand_split in node.getElementsByTagName("tag")[nd_num].getAttribute(
                                    "v").lower().split():
                                for shop_name_split in name.lower().split():
                                    if tag_brand_split == shop_name_split:
                                        name_match = True
                                        break

                # the name has to match, or maybe the way just uses another shop's information
                if name_match:
                    shop_match = True

                    # store this node's index for further use
                    node_temp = node
                    break

    if shop_match is False:
        print('The shop with the given information can not be found. Use a sample shop data instead.')

    return shop_match, node_temp

osm_file = "C:/Users/86781/PycharmProjects/pythonProject/data/test_area.osm"

DOMTree = xml.dom.minidom.parse(osm_file)
osm = DOMTree.documentElement

# import all way and node elements
ways = osm.getElementsByTagName("way")
nodes = osm.getElementsByTagName("node")

check_pure_node(nodes, 10.5213742, 52.2646307, 0.0003, 'Sack', '5', 'Go Asia')

pass