import pandas as pd


def load_excel(filepath, sheet='Tabelle1'):
    """This function can be used to load a whole Excel sheet directly from the path and return contained data."""

    # Unless specified, the path for input excel data should in the /data folder.
    # Falls nicht gegeben, 'C:/Users/86781/PycharmProjects/pythonProject/venv/data/' wird hier genutzt.
    # Because of the region and language setting of Office suite, the sheet name of an Excel file can be
    # different. English='Sheet1', German='Tabelle1'
    data = pd.read_excel(filepath, sheet_name=sheet)
    return data


def get_excel_address_state(filepath, sheet):
    """This function aims only to return the state of the shops from a given .xlsx file."""

    # the given .xlsx file is generated from the result of Nominatim server,
    # so the third column is always the row with the state record.
    data = pd.read_excel(filepath, sheet_name=sheet)
    state_name = ["baden-württemberg", "baden-wuerttemberg", "bayern", "berlin",
                  "brandenburg", "bremen", "hamburg", "hessen", "mecklenburg-vorpommern",
                  "niedersachsen", "nordrhein-westfalen", "rheinland-pfalz", "saarland",
                  "sachsen", "sachsen-anhalt", "schleswig-holstein", "thüringen", "thueringen"]

    # Here we do not consider the situation that inside a .xlsx file, there are shops from different states
    state_list = []

    for i in range(len(data)):
        if data.values[i][2].split(", ")[-3].lower() in state_name:
            state = data.values[i][2].split(", ")[-3].lower()
            state_list.append(state)
        else:
            state_list.append("NA")

    def most_common(list):
        return max(set(list), key=list.count)

    # find the most common element in the list as the state
    if most_common(state_list) != 'NA':
        return most_common(state_list)
    else:
        print("State record error. Please input the state manually.")
        state = input("state=?")
        return state
