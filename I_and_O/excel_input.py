import pandas as pd


def load_excel(filename, sheet='Tabelle1', path='C:/Users/86781/PycharmProjects/pythonProject/data/'):
    """This funktion can be used to load a whole Excel sheet directly from the path and return contained data."""

    # Unless specified, the path for input excel data should in the /data folder.
    # Falls nicht gegeben, 'C:/Users/86781/PycharmProjects/pythonProject/venv/data/' wird hier genutzt.
    # Because of the region and language setting of Office suite, the sheet name of an Excel file can be
    # different. English='Sheet1', German='Tabelle1'
    data = pd.read_excel(path + filename, sheet_name=sheet)
    return data


def get_excel_celldata(filename, cell_row, cell_column, sheet='Tabelle1',
                       path='C:/Users/86781/PycharmProjects/pythonProject/venv/data/'):
    """This funktion can be used to get access to a cell value of the Excel file quickly.
    Attention: All excel rows and columns starts with 0."""

    data = pd.read_excel(path + filename, sheet_name=sheet)
    celldata = data.iloc[[cell_row], [cell_column]]
    return celldata
