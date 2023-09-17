import pandas as pd

def set_excel(data, filename, sheet='Tabelle1', path='C:/Users/86781/PycharmProjects/pythonProject/venv/data/'):
    """This funktion can be used to write a pandas dataframe formatted Dictionary into the excel file."""

    # The Dictionary "data" passed into this funktion should in pandas dataframe format.
    # Example: data = {'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9], index=['Portland', 'Berkeley', 'New York']}
    dt = pd.DataFrame.from_dict(data)

    # Because of the region and language setting of Office suite, the sheet name of a excel file can be
    # different. English='Sheet1', German='Tabelle1'
    dt.to_excel(path + filename, sheet_name=sheet)
    print('Write to excel file success.')
    print('-----------------------------------------------------------------------------------------------------------')


def set_excel_column(titel, data, filename, sheet='Tabelle1', path='C:/Users/86781/PycharmProjects/pythonProject/venv/data/'):
    df = pd.read_excel(path + filename)

    df = df.assign(titel = data)

    df.to_excel(path + filename, sheet_name=sheet, index=False)
    print('Write to excel file success.')
    print('-----------------------------------------------------------------------------------------------------------')
