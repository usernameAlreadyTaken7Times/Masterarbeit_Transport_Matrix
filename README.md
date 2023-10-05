# Transport matrix

This project aims to generate a transport matrix for urban
logistics transport vehicles.
(Calculation program entrance at ``main``)

Apart from the main calculation program, two other scripts, 
which can be of help to the workflow with Anylogic-Program,
are also provided.
They are the ``Anylogic_shop_and_distance_generator`` and 
the ``Anylogic_output_csv_process`` scripts.
Both of the scripts are located in the folder ``Anylogic_data_process``.

The first script ``Anylogic_shop_and_distance_generator.py`` can be used to generate the essential data file,
which can be used by two Anylogic-Programs to build their databases.
The second script ``Anylogic_output_csv_process.py`` aims to use two .csv
result files from Anylogic-Programs and draw curve graphs of the fleet's utilization rate.

So the workflow should be used in such way:
1. run the ``Anylogic_shop_and_distance_generator.py`` script to generate/update data for Anylogic-Programs;
2. run the ``main.py`` script for the calculation of the transport matrix;
3. run the two Anylogic-Programs to get the output result .csv files;
4. run the ``Anylogic_output_csv_process.py`` script to draw graphs.

### Explanation of each folder and important scripts

Basically, every script under the same path has a similar working task.

#### Path ``algorithm``

This path stores the sub-functions of the main calculation program.
They are all necessary to the Program and should not be deleted.
Most sub-functions aim to retrieve the data from an .xlsx file,
while others may be used to cut the test area and calculate relevant parameters.

#### Path ``alternative_Nominatim``

Two scripts under this path, ``geocode_imn`` is not part of the program.
It is an example code from Mr. Cruz to show how to build the result.
The other one ``get_shop_list_Nominatim`` can be used to retrieve shop list data
from offline/online Nominatim Server.

#### Path ``Anylogic_data_process``

Scripts under this path can be of help to the data exchange from/to Anylogic-Program.
The usages of these scripts are explained before.
The ``set_loations`` script is just a sub-functions storing script for the file generator.

#### Path ``data``

No scripts are stored under this path.
This folder stores program-relevant data only,
including the .xlsx data files, downloaded .pbf files and people density .csv files.

#### Path ``IO``

Only sub-functions relevant to data pre-processing and read/write stored in this folder.

#### Path ``osm_object_Methods``

The functions about .osm data processing are stored here,
including .pbf file extraction scripts, the searching functions...

#### Path ``settings``

This folder stores two configuration files about all possible switches and strings of file paths.
They are called by the main calculation program and two other scripts related to the Anylogic-Programs.

#### Path ``update``

The files under this path are the update programs for .pbf files and people density .csv file.
They may be called in the main calculation program, depending on the configuration files.
When they are active, they search for the data and try to download the version on the online server.
URL build-in in the scripts.

#### Script ``main``

``main`` is the entrance of the calculation program. 
Generally speaking, this script can be divided into several parts:
inspection, updating, dividing the test area,
downloading the experimental area store list,
finding matches in the osm file, calculating relevant parameters,
calculating the number of customers,
and converting it into store goods demand.

First the script tests the inputs are valid or not, 
then try to update files (when it is told to in conf file).
The input shop area's boundary coordinates are then used to 
calculate different test areas, and use the test area 2's boundary
to download the shop list from Nominatim server.

Then extract the area's osm file with the .pbf file for further distance database's generating.
The shop list downloaded from Nominatim server is also used to search for .osm file for match.
When finding a match, then calculate the building area and influence coefficient of the shop, 
and calculate the attractiveness of the shop.
In the end, the distance database and test area blocks' information are used to calculte the customer
number visiting shops.
These customer number can be converted to shop good demand later with formulas.

#### Script ``Anylogic_shop_and_distance_generator``

``Anylogic_shop_and_distance_generator`` can be used to generate the need files for Anylogic-Programs.
Those include the shop location file ``location.xlsx``,
the distributor location file ``distributor_locations.xlsx``,
the logistic center location file ``logistic_center_locations.xlsx``, 
the distance database file ``distances.xlsx``,
the vehicle info file ``v_info.xlsx`` and a .txt file with the map center.
Except the last one, these files are needed by the Anylogic-Programs to build their database, 
which is an essential part for the running of the program.

The files for both Anylogic-Programs should be identical.
However, the Anylogic-Program with new method (good demand)
should use a different .xlsx file with shop demand, 
instead the original shop location file ``location.xlsx``.
So the Anylogic-Program with the new method gets a similar .xlsx file with good demand, 
called ``locations_with_good_weight.xlsx``.
This file is generated after running the main calculation program.

#### Script ``Anylogic_output_csv_process``

This script ``Anylogic_output_csv_process`` aims to deal with the output .csv files from the two Anylogic-Programs.
First, it reads two .csv files and then split it with day records.
After getting one day's record, then split this day's records with different trucks' ID.
For every truck, the capacity changes will be calculated and added to the whole fleet's capacity changesets,
and eventually, the changeset of one day's record is available.

Drawing the curve of capacity changesets of Anylogic-Programs with new and old method,
the tendency can be shown in the graphs.

