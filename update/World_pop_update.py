import sys
import requests
import math
import os
import zipfile
import pandas


def file_download(url, path, filename):
    """This function aims to download a file."""
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


if __name__ == '__main__':
    """This function can be used to download the population density data from the chosen website. Then the files are 
    merged into a combined .csv file and stored in upper path for further use. """
    path_file = '../data/pop_den/'

    # Here are the filename and links for other online file/database in case of needs.
    filename_light = ''
    url_light = ''

    for data_year in range(2000, 2021):

        # The population data and link can be modified here.
        filename_pop = 'deu_pd_' + str(data_year) + '_1km_UNadj_ASCII_XYZ.zip'
        filename_pop_csv = 'deu_pd_' + str(data_year) + '_1km_UNadj_ASCII_XYZ.csv'
        url_pop = 'https://data.worldpop.org/GIS/Population_Density/Global_2000_2020_1km_UNadj/' + str(data_year)\
                  + '/DEU/deu_pd_' + str(data_year) + '_1km_UNadj_ASCII_XYZ.zip'

        # check if the file is already there
        if os.path.exists(path_file + filename_pop_csv):
            print('The file of year ' + str(data_year) + ' already exists and does not need to be downloaded.')
            print('----------------------------------------------------------------------------------------------------'
                  '-------')
            continue
        else:
            # download the file from server and unzip the file
            file_download(url_pop, path_file, filename_pop)
            with zipfile.ZipFile(path_file + filename_pop, "r") as zip_ref:
                zip_ref.extractall(path_file)
            os.remove(path_file + filename_pop)
            print('The file of year ' + str(data_year) + ' was successfully downloaded and converted.')
            print('----------------------------------------------------------------------------------------------------'
                  '--------')

    print('Update program finish, merging process begins.')
    print('***********************************************************************************************************')

    # start to merge the data into a combined .csv file

    # check if the merged_csv file is already existed in the upper path
    if os.path.exists(path_file[0:-8] + 'pop_dsy_merged.csv'):
        os.remove(path_file[0:-8] + 'pop_dsy_merged.csv')
        print('Old population density file discarded. Creating new file.')
    else:
        print('No population density file found. Creating new file.')

    # create a basic .csv file with coordinates as index
    csvFile = pandas.read_csv(path_file + filename_pop_csv)
    csvFile = csvFile.drop(csvFile.columns[2], axis=1)

    # read all the .csv files and copy the data into the merged .csv file
    for data_year in range(2000, 2021):
        file_name = 'deu_pd_' + str(data_year) + '_1km_UNadj_ASCII_XYZ.csv'
        new_csvFile = pandas.read_csv(path_file + file_name)
        new_csvFile = new_csvFile.drop(['X', 'Y'], axis=1)
        new_csvFile.columns = [str(data_year)]
        csvFile = pandas.concat([csvFile, new_csvFile], axis=1)

    # save the file in the upper path
    csvFile.to_csv(path_file[0:-8] + 'pop_dsy_merged.csv', index=False)

    print('New population density .csv file created. Merge process finish.')
    sys.exit(0)
