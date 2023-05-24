import os.path

import osmium
import sys
import pandas as pd
import openpyxl


class NamesHandler(osmium.SimpleHandler):
    """This is the method for searching given keyword nodes in a .pbf file.
    The time depends on hardware strength, the searching keyword and the .pbf file size.
    These code was tested on a laptop with intel i7-12700, 32Gb memory with a 3,81 Gb .pbf file,
    and some results are listed below.
    --------------------------------------------------------------------------------------------------------------------
    It takes about 36 minutes to find 940 nodes meet the criteria (keyword = 'Rewe').
    It takes about 22 minutes to find 728 nodes meet the criteria (keyword = 'Kaufland').
    It takes about 93 minutes to find 1754 nodes meet the criteria (keyword = 'Rossmann').
    --------------------------------------------------------------------------------------------------------------------
    The occupation of this task stayed around 15% all the time."""
    def __init__(self, path, xlsxfilename, keyword):
        osmium.SimpleHandler.__init__(self)

        # variables init
        self.num_nodes = 0
        self.dict2 = {}
        self.dict2.update({'name': ''})
        self.dict2.update({'longitude': ''})
        self.dict2.update({'latitude': ''})

        # link outside variables to the ones used in the method
        self.xlsx_path = path
        self.filename = xlsxfilename
        self.searching_name = keyword

        # check if there is already .xlsx file in tha path, if yes, delete the file
        if os.path.exists(self.xlsx_path + self.filename):
            os.remove(self.xlsx_path + self.filename)

    def node(self, n):

        # test if the node have a 'name' attribute
        if 'name' in n.tags:

            # test if the 'name' attribute have the keyword inside
            if self.searching_name in n.tags['name'].split():

                # relative numbers init, dict1 is the dictionary for the output of properties into .xlsx file
                self.num_nodes += 1
                dict1 = {}

                # print the longitude and latitude for the chosen points
                print(f'{n.location}: ' + n.tags['name'])
                print('----------------------------------')

                # set the first 3 properties of dict1 as name, longitude and latitude
                dict1.update({'name': n.tags['name']})
                dict1.update({'longitude': n.location.lon})
                dict1.update({'latitude': n.location.lat})

                # a cycle for the output of all properties of the node, the building of universal keys dictionary is
                # also in this cycle.
                for a in n.tags:
                    # the first column is the key and the second is the value
                    key = str(a).split('=')[0]
                    value = str(a).split('=')[1]

                    # wirte the keys and values into dict1
                    dict1.update({key: value})

                    # try to build a universal keys dictionary for further use
                    if self.dict2.__contains__(key):
                        pass
                    else:
                        self.dict2.update({key: ''})

                sheetname = 'Tabelle_Laden' + str(self.num_nodes)

                # output the dictionary for every node into their worksheet
                df = pd.Series(dict1, name='Ausgabe')
                df.index.name = 'Eigenschaften'
                df.reset_index()

                # read the file data and append new data onto it
                if os.path.exists(self.xlsx_path + self.filename):
                    writer = pd.ExcelWriter(self.xlsx_path + self.filename, mode='a', engine='openpyxl')
                else:
                    print('No .xlsx file in the path found. Creating a .xlsx file now.')
                    wb = openpyxl.Workbook()
                    # sheet_name = wb.sheetnames
                    wb.save(filename=self.xlsx_path + self.filename)
                    writer = pd.ExcelWriter(self.xlsx_path + self.filename, mode='a', engine='openpyxl')

                # save the file
                df.to_excel(writer, sheet_name=sheetname)
                writer._save()
                print(f'{self.num_nodes} nodes found. Please wait.')
            else:
                pass
        else:
            pass


def get_excel_report(xlsxpath, xlsxfilename,
                     search_name,
                     pbfpath, pbffilename):
    """This funktion is the first part of creating the overlook worksheet.
    Five parameters are needed here: the path and the name of the xlsx & pbf file,
    as well as the search keyword. """

    # link basic variables
    searching_name = search_name
    xlsx_path = xlsxpath
    filename = xlsxfilename

    # call the method
    handler = NamesHandler(xlsx_path, filename, searching_name)
    handler.apply_file(pbfpath+pbffilename)

    # sorting the universal key dictionary, this list is all the tags relevant to the nodes and should be used for
    # reformating the worksheet
    list3 = sorted(handler.dict2.items(), reverse=False)
    num = handler.num_nodes

    print(f'{handler.num_nodes} Nodes found, collecting data from .pbf file finish.')

    return list3, num


if __name__ == '__main__':



    sys.exit(0)
