import requests
import os
import time
import hashlib
import math
from bs4 import BeautifulSoup


def md5_download(url, path, filename):
    """This funktion aims to download .md5 hash file."""
    response = requests.get(url)
    open(path + filename, 'wb').write(response.content)


def pbf_download(url, path, filename):
    """This funktion aims to download .pbf file.
    Because the .pbf file is always relatively big, a progress display is applied."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    num_blocks = math.ceil(total_size / block_size)

    with open(path + filename, 'wb') as f:
        for i, chunk in enumerate(response.iter_content(block_size)):
            f.write(chunk)
            progress = (i + 1) / num_blocks
            print(f'\r{filename} download progress: {progress:.2%}', end='')

    print(f'\nDownload complete: {filename}\n')


def get_pbf_creation_time(path, filename):
    """This funktion returns the creation time of a given-path file."""
    creation_time = os.path.getctime(path + filename)
    # viable formatted_time can be directly outputted to screen and read.
    formatted_time = time.ctime(creation_time)
    return formatted_time


def get_pbf_md5(path, filename, mode):
    """This funktion returns the md5 hash of the downloaded local .pbf file, yet the md5 hash calculating of a 3Gb data
     on a low-performance computer could take pretty long time.

     For mode 1, only the md5 hash will be returned. For mode 2, the md5 hash and the calculating time together
     will be returned."""
    start_time = time.time()
    with open(path + filename, 'rb') as f:
        file_data = f.read()
        md5_hash = hashlib.md5(file_data).hexdigest()
    end_time = time.time()
    elapsed_time = end_time - start_time
    if mode == 1:
        return md5_hash
    if mode == 2:
        return md5_hash, elapsed_time
    if mode != 1 and mode != 2:
        print('parameter unfit, please choose from 1 and 2.')


def get_md5_infile(file):
    """This funktion is used to read md5 from a txt file. According to the standard, the first 32 characters
     are the md5 hash of the .pbf file."""
    with open(file, 'r') as f:
        data = f.read(32)
    return data


def pbf_update(path, pbf_filename, pbf_url):
    """This funktion can be used to check and update a .pbf file.
     :param path: The path where the .pbf file is stored.
     :param pbf_filename: The name of the .pbf file.
     :param pbf_url: The url where the .pbf can be downloaded.
     """
    md5_filename = pbf_filename + '.md5'
    md5_url = pbf_url + '.md5'
    pbf_filename_without_suffix = pbf_filename[0:-8]
    md5_filename_without_suffix = md5_filename[0:-12]

    print('***********************************************************************************************************')
    print(f'Checking {pbf_filename_without_suffix} .pbf file, please wait.')
    print('***********************************************************************************************************')

    # first check if the .pbf file is already in the path
    if os.path.exists(path + pbf_filename):
        print(f'The {pbf_filename_without_suffix}.pbf file exists.')

        # check if an old .md5 hash exist in the path
        if os.path.exists(path + md5_filename):
            os.remove(path + md5_filename)
            print(f'Old {md5_filename_without_suffix} md5 hash deleted successfully.')
        print('-------------------------------------------------------------------------------------------------------'
              '----')
        print(f'The {md5_filename_without_suffix} md5-hash '
              f'of .pbf file is now being calculated to determine the file version.')
        print('-------------------------------------------------------------------------------------------------------'
              '----')

        # calculate the md5 hash of the existing .pbf file
        pbf_md5 = get_pbf_md5(path, pbf_filename, 1)
        print(f'The {md5_filename_without_suffix} md5-hash of '
              f'local  {pbf_filename_without_suffix} .pbf file is {pbf_md5}')

        # requesting the up-to-date .pbf file's md5
        md5_download(md5_url, path, md5_filename)
        pbf_md5_web = get_md5_infile(path + md5_filename)
        print(f'The {md5_filename_without_suffix} md5-hash of '
              f'online {pbf_filename_without_suffix} .pbf file is {pbf_md5_web}')
        print('-------------------------------------------------------------------------------------------------------'
              '----')

        # check if these 2 md5 the same
        if pbf_md5 != pbf_md5_web:
            pbf_creation_time = get_pbf_creation_time(path, pbf_filename)
            print(f'The {pbf_filename_without_suffix} .pbf file was '
                  f'created on {pbf_creation_time} and needs to be updated. Processing...')

            # delete the old .pbf file
            os.remove(path + pbf_filename)

            # update .pbf file
            pbf_download(pbf_url, path, pbf_filename)

            # check if the newly-downloaded file is updated
            pbf_md5 = get_pbf_md5(path, pbf_filename, 1)
            if pbf_md5 == pbf_md5_web:
                print(f'{pbf_filename_without_suffix}.pbf file was updated successfully.')
                print('-----------------------------------------------------------------------------------------------'
                      '------------\n\n')

            else:
                print(f'{pbf_filename_without_suffix}.pbf file was updated unsuccessfully.')
                print('-----------------------------------------------------------------------------------------------'
                      '------------\n\n')
        else:
            print(f'The {pbf_filename_without_suffix} .pbf file is already up-to-date. Update not needed.')
            print('---------------------------------------------------------------------------------------------------'
                  '--------\n\n')
    else:
        print(f'The {pbf_filename_without_suffix} .pbf file does not exist. '
              f'The file will be requested from the website.')
        print('-------------------------------------------------------------------------------------------------------'
              '----')

        # update .pbf file
        pbf_download(pbf_url, path, pbf_filename)

        # check if the newly-downloaded file is updated
        md5_download(md5_url, path, md5_filename)
        pbf_md5_web = get_md5_infile(path + md5_filename)
        pbf_md5 = get_pbf_md5(path, pbf_filename, 1)
        if pbf_md5 == pbf_md5_web:
            print(f'{pbf_filename_without_suffix}.pbf file was updated successfully.')
            print('---------------------------------------------------------------------------------------------------'
                  '--------\n\n')
        else:
            print(f'{pbf_filename_without_suffix}.pbf file was not updated unsuccessfully.')
            print('---------------------------------------------------------------------------------------------------'
                  '--------\n\n')
    print(f'Update for {pbf_filename_without_suffix} file finish.')
    print('***********************************************************************************************************')


def get_pbf_weblinks(level):
    """This funktion is used to get all .pbf links on the osm website.
    :param level: Level determines which level of administrative districts
        (countries-/-1, country-/0, province-/1 or city-area/2) would be downloaded.
    :return: A list of all file names and their links fill the requirements
    """

    # variables init
    num = 0
    name = ['']
    url = ['']

    # level == -1 means the downloaded .pbf file is fit for the 3 german-speaking countries.
    if level == -1:
        # German-speaking area: Germany, Austria and Switzerland
        file_url = 'https://download.geofabrik.de/europe/dach-latest.osm.pbf'
        file_name = 'dach-latest.osm.pbf'
        name[num] = file_name
        url[num] = file_url
        print(f'All 1 .pbf files found.')
        print('-------------------------------------------------------------------------------------------------------'
              '----')
        return name, url

    # level == 0 means the downloaded .pbf file is ft for Germany only.
    if level == 0:
        file_url = 'https://download.geofabrik.de/europe/germany-latest.osm.pbf'
        file_name = 'germany-latest.osm.pbf'
        name[num] = file_name
        url[num] = file_url
        print(f'All 1 .pbf files found.')
        print('-------------------------------------------------------------------------------------------------------'
              '----')
        return name, url

    # For level == 1, all the subregions of Germany(provinces) are separately downloaded.
    if level == 1:

        # the website of german osm .pbf files
        original_url = 'https://download.geofabrik.de/europe/germany/'

        # use Beautifulsoup to get all the link trees under the index
        response = requests.get(original_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        # check the url links and find the files which end with "-latest.osm.pbf"
        for link in links:
            file_url = original_url + link['href']
            if file_url.endswith('-latest.osm.pbf'):
                file_name = os.path.basename(file_url)
                name.insert(num, file_name)
                url.insert(num, file_url)
                num = num + 1
        print(f'All {num} .pbf files found.')
        print('-------------------------------------------------------------------------------------------------------'
              '----')
        del url[num]
        del name[num]
        return name, url

    # For level == 2, all the subregions of german provinces(districts) are separately downloaded.
    # However, only 3 provinces(Baden-Württemberg, Bayern und Nordrehein-Westfalen) have subregions
    # on Openstreetmap website. So here these links are stored in a list. If there are modifications
    # on Openstreetmap, in the future, similar code can be added or deleted here.
    if level == 2:
        # the website of german osm .pbf files
        original_url = ['https://download.geofabrik.de/europe/germany/',
                        'https://download.geofabrik.de/europe/germany/baden-wuerttemberg/',
                        'https://download.geofabrik.de/europe/germany/bayern/',
                        'https://download.geofabrik.de/europe/germany/nordrhein-westfalen/']

        for url_temp in original_url:

            # use Beautifulsoup to get all the link trees under the index
            response = requests.get(url_temp)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')

            # check the url links and find the files which end with "-latest.osm.pbf"
            for link in links:
                file_url = url_temp + link['href']
                if file_url.endswith('-latest.osm.pbf'):
                    file_name = os.path.basename(file_url)
                    name.insert(num, file_name)
                    url.insert(num, file_url)
                    num = num + 1

        # remove the 3 provinces that are downloaded twice (in different level)
        name.remove('baden-wuerttemberg-latest.osm.pbf')
        name.remove('bayern-latest.osm.pbf')
        name.remove('nordrhein-westfalen-latest.osm.pbf')
        url.remove('https://download.geofabrik.de/europe/germany/baden-wuerttemberg-latest.osm.pbf')
        url.remove('https://download.geofabrik.de/europe/germany/bayern-latest.osm.pbf')
        url.remove('https://download.geofabrik.de/europe/germany/nordrhein-westfalen-latest.osm.pbf')

        print(f'All {num-3} .pbf file names and links found.')
        print('-------------------------------------------------------------------------------------------------------'
              '----')
        del url[num-3]
        del name[num-3]
        return name, url

    if level != -1 and level != 0 and level != 1 and level != 2:
        print('parameter unfit, please choose from -1, 0, 1, 2.')
        print('-------------------------------------------------------------------------------------------------------'
              '----')
        return [''], ['']


def pbf_update_program(path, area=0):
    """This .py program can be used to get the .pbf file urls and determine weather local .pbf files are up-to-date. 
    If not, it will automatically update the .pbf file."""

    # Area shows that which level of area is used in the project. Area=-1~3 countries(Deutschzone); area=0~germany only;
    # Area=1~germany provinces; Area=2~much lower level of germany provinces, by default area=0

    pbf_name, pbf_url = get_pbf_weblinks(area)
    t = 0
    while t < len(pbf_name):
        # print(t, pbf_name[t], pbf_url[t])
        pbf_update(path, pbf_name[t], pbf_url[t])
        t = t + 1
    print('PBF file updating finish.')
    print('***********************************************************************************************************')


def pbf_Europe_update_program(path):
    """This function can be used to get the Europe's .pbf file."""

    # for europe's .pbf file, no checking md5 and then update support.
    pbf_name = "europe-latest.osm.pbf"
    pbf_url = "https://download.geofabrik.de/europe-latest.osm.pbf"
    if os.path.exists(path + pbf_name):
        print("No update needed, file already exists.")
    else:
        pbf_download(path, pbf_name, pbf_url)
        print('Europe PBF file updating finish.')

    print('***********************************************************************************************************')

