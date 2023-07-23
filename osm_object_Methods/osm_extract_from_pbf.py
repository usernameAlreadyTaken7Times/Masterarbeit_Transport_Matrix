import subprocess
import os


def osm_extract_from_pbf(min_lon, min_lat, max_lon, max_lat, osm_tool_path,
                         pbf_file_path="C:/Users/86781/PycharmProjects/pythonProject/data/osm/",
                         pbf_file_name="germany-latest.osm.pbf",
                         osm_file_path="C:/Users/86781/PycharmProjects/pythonProject/data/",
                         osm_file_name="test_area.osm"):
    """This function can be used to extract data of a specific area whose coordinates should be given. Please note: the
    function involves command-line tool "osmium" and use it to extract data, so special characters, including spaces and
    commas, should be checked before running thin function.
    :param float min_lon: The minimum longitude of the test square area,
    :param float min_lat: the minimum latitude of the test square area,
    :param float max_lon: the maximum longitude of the test square area,
    :param float max_lat: the maximum latitude of the test square area,
    :param str osm_tool_path: the path, in which the osmium command-line tool is located,
    :param str pbf_file_path: the path, in which the pbf file is located,
    :param str pbf_file_name: .pbf file's name, in which should contain all test area's data,
    :param str osm_file_path: the path, in which the .osm file should be stored,
    :param str osm_file_name: .osm file's store name.
    """

    # check if the test_area.osm file already exists
    if os.path.exists(osm_file_path+osm_file_name):
        os.remove(osm_file_path+osm_file_name)

    # for some path which is not set as running environments, .\ is necessary
    osm_command = '.\\osmium.exe'

    # bounding box of the chosen test area
    bbox = f"{str(min_lon)},{str(min_lat)},{str(max_lon)},{str(max_lat)}"

    # arguments of osmium command-line tool
    arg = ' extract -b ' + bbox + ' ' + pbf_file_path + pbf_file_name + ' -o ' + osm_file_path + osm_file_name

    cmd = osm_tool_path + osm_command + arg

    subprocess.run(cmd)
    print('.osm file extracted and stored.')

