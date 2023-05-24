import os.path
import pandas as pd
import openpyxl
import sys

from I_and_O.excel_input import load_excel


def get_pre_processing_excel(filename, sheet='Tabelle1', path='C:/Users/86781/PycharmProjects/pythonProject/venv/data/'):
    """This funktion should be uesd to preprocess the input .xlsx file, which caitains the names, addresses of the shop
    and the geo-coordinates(for thoes shops which can be found in the .pbf file) for further use.
    The output of this funktion should be a processed .xlsx file with fixed format, for example:

    |Nr.---|Name----|City------------|street-------------|Number-----|coordinate_Lat----------|coordinate_Log--------|
    |1.    |Rewe    |Braunschweig    |Rebenring          |63         |xx.xxxxxxxxxxx          |xx.xxxxxxxxxxx        |
    ------------------------------------------------------------------------------------------------------------------
    |2.    |Rewe    |Braunschweig    |Wendenring         |1          |xx.xxxxxxxxxxx          |xx.xxxxxxxxxxx        |
    ------------------------------------------------------------------------------------------------------------------
    |3.    |IMN     |Braunschweig    |Langer Kamp        |19a        |xx.xxxxxxxxxxx          |xx.xxxxxxxxxxx        |
    ------------------------------------------------------------------------------------------------------------------
    ......
    ......
    ------------------------------------------------------------------------------------------------------------------
    |x.    |xxx     |xxxxxxxxxxxx    |xxxxxxxxxxx        |xxx        |xx.xxxxxxxxxxx          |xx.xxxxxxxxxxx        |

    (Take Nr. 3 as example, the coordinates is not available from the .pbf file. It will be completed in the next step
    using Geocoding method.)

    This is the first processing step for the input .xlsx file. In the following step, the skript deals with the shops
    which do not have coordinates yet.
    """
    data = load_excel(filename, sheet, path)





