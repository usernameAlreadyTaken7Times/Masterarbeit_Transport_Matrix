import sys
import pandas as pd
import os.path

def reformat_excel_report(path, file_name, list, num_node):
    """This funktion is the second part of excel report, aiming to reformat the existing .xlsx file
    containing shop information.
    This funktion works only on the reformation, so the speed should be fast.
    Tests on laptop with intel i7-12700 with 32Gb memory had been run.
    For workbook with about 800 worksheets takes no more than 3 minutes."""

    # variable init
    xlsx_path = path
    filename = file_name
    list1 = list

    # build pandas dataframe with the ordered list
    df1 = pd.DataFrame(list1)

    # for every sheet containing information of a new shop, the tranvsing is necessary
    for sheet_num in range(1, num_node+1):
        writer1 = pd.read_excel(io=xlsx_path + filename, sheet_name='Tabelle_Laden' + str(sheet_num), usecols="A,B")

        dict_writer = {}

        # init the writer with '-'
        for num_node_tags in range(0, len(list1)):
            dict_writer.update({list1[num_node_tags]: '-'})

        # search the 'Eigenschaften' of nodes and check if it match the key of universal keys dictionary
        for num_tag in range(0, len(writer1.Eigenschaften)):
            for num_node_tags1 in range(0, len(list1)):

                # if the key matches, then write the valus into 'writer' and wait for writing into the file
                if list1[num_node_tags1][0] == writer1.Eigenschaften[num_tag]:
                    dict_writer.update({list1[num_node_tags1]: writer1.Ausgabe[num_tag]})

        # output the dictionary for every node into their worksheet
        df = pd.Series(dict_writer, name='Ausgabe')
        df.index.name = 'Eigenschaften'
        df.reset_index()

        # 'new_data' is the information column for a newly accaried shop
        new_data = df.values

        # and is here attached to the end of df1, which will be later printed onto the default worksheet 'sheet0'
        df1.insert(sheet_num, "Laden" + str(sheet_num), new_data, allow_duplicates=True)
        print(f'working on sheet {sheet_num}')
        pass

    # after the whole cycle, df1 contains all the information of shops and now can be written into .xlsx file
    df1.to_excel(xlsx_path + filename, sheet_name='sheet0', index=False, header=True)
    print('Reformation success.')


if __name__ == '__main__':

    sys.exit(0)