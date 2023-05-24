import requests
import pandas as pd


def write_locations(store, city, max_samples, ip, filename):
    query = f"{store}+{city}"
    url = (f"http://{ip}/nominatim/search.php?q={query}"
           f"&format=jsonv2&limit={max_samples}")
    req = requests.get(url).json()
    
    retailers = pd.DataFrame(
        columns=["lat", "lon", "address"], index=range(len(req)))
    
    for row in range(len(req)):
        retailers.at[row, "lat"] = float(req[row]["lat"])
        retailers.at[row, "lon"] = float(req[row]["lon"])
        retailers.at[row, "address"] = req[row]["display_name"]
    
    retailers.to_excel(filename, sheet_name="stores", index=False)


if __name__ == '__main__':
    ip = "134.169.70.84" # IP address of the Nominatim server (may change)
    city = "Braunschweig"
    store = "Rewe"
    filename = "store_locations.xlsx"
    max_samples = 100
    write_locations(store, city, max_samples, ip, filename)
