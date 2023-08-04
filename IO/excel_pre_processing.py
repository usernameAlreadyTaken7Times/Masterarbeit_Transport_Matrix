from IO.excel_input import load_excel


def get_pre_processing_excel(origin_path, origin_filename, sheet_name, store_path, store_name, store_sheet_name):
    """This funktion aims to pre-process the input .xlsx file, which contains the addresses and the geo-coordinates
     of the shops.
     :param str origin_path: The file path, where the to-be-processed .xlsx file is located,
     :param str origin_filename: the file name,
     :param str sheet_name: the .xlsx file sheet name,
     :param str store_name: the file name to be stored in /data/ folder,
     :param str store_path: the file path, actually the /data/ folder,
     :param str store_sheet_name: the stored .xlsx file sheet name.
    """

    data = load_excel(origin_path+origin_filename, sheet_name)

    # we assume the to-be-processed .xlsx file is in the such format: Nr-ID-lat-lon-address,
    # yet the output format should be lon-lat-address

    # drop unnecessary columns
    data = data.drop(columns=['Unnamed: 0', 'id'])

    # change columns' places
    data = data.loc[:, ['lon', 'lat', 'address']]

    # save the data to an .xlsx file for further use
    data.to_excel(store_path + store_name, store_sheet_name, index=False)

# # test code
# get_pre_processing_excel("C:/Users/86781/PycharmProjects/pythonProject/", "locations.xlsx",
#                          "stores", "C:/Users/86781/PycharmProjects/pythonProject/data/",
#                          "locations.xlsx", "stores")
# pass






