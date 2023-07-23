# Workflow

## 1. parameters init

get all parameters ready

TBD: conf. file

## 2. get involved shop information


### 2.1 get coordinates with the init shop name list

Normally, this step is not part of the project, because the coordinates
of the test shops should be offered before the program starts in a
.xlsx file.

Or the original file could only contain the name and address of 
the shops. Under such circumstances, 2.1 is necessary.

#### 2.1.1 from Nominatim Server

Use the IMN's Nominatim server to search for the coordinates(fast).
However, some coordinates point on Nominatim can differ from those
in .osm.pbf files. So in this case, an offset of coordinates.(+-0.003)

`alternative_Nominativ.get_coordinate_from_address_Nominatim`


#### 2.1.2 from .pbf file

use the .osm.pbf file to search for the coordinates(slow)

due to (unkonwn)_**(really?)**_ coordinates of the shop, all
.pbf file needs to be searched.

`alternative_osm.get_coordinate_from_address`

~~(backup)~~

need to be rearranged

The main functions already exist but still need to be 
adjusted to fit the main program's demand.

### 2.2 use the coordinates to get information about involved blocks

maximum longitude and latitude from shop list

`algorith.calc_test_area_idx_info`

### 2.3 use the involved blocks' coordinates and extract the test area's osm file

`osm_object_Methods.osm_extract_from_pbf`

### 2.4 use the 2.2 blocks' geo coordinates to search for other involved shops' coordinates

blocks' coordinates from 2.2, +-0.0415?(half block side length)

`alternative_Nominatim.get_shop_list_Nominatim`


#### 2.4.1 from Nominatim Server

search for all shops' list in certain area

`alternative_Nominatim.get_shop_list_Nominatim`

#### 2.4.2 from .pbf file

use the 2.3 osm file to traverse and coordinates as bounding box

`alternative_osm.get_shop_list_osm`

(backup)

### 2.5 use the 2.1&2.4 coordinates to get shop information from .pbf file (area, facility, grade etc.)

from .osm.pbf, google grade into a .xlsx file

`osm_object_Methods.get_shop_info_osm`
`osm_object_Methods.get_shop_way_ref_osm_xml`


## 3. calculate every shop attraction influence using attractiveness formula with shop information from 2.5

`algorithm.calc_shop_attraction`


## 4. use Huff Method to calculate the possibility for population on each block to go to a specific shop

### 4.1 calculate the driving distance from each block to shop(pbf)

`osm_object_Methodes.get_route_distance`

### ~~4.2 analyse the relationship between different marks (Rewe-Lidi, Commodity substitution rate)~~

~~use wholesale amount / retail store number = avg(Brand_shop)
and take that shop information as default to compare with each
other.~~

~~**TBD**~~

### 4.3 Huff Method calculation

`algorithm.get_test_area_customer_shop_possibility`

## 5. get retail amount and cargo volume

### 5.0 preprocess the BIP_handel from 2 statistic source

`IO.Pre_process_BIP_handel`

### 5.1 use .csv file and data fitting to get average retail sale amount on prediction year for the chosen state

`algorithm.calc_retail_average`

### 5.2 get test district whole retail amount on prediction year(5.1*population on blocks)

`algorithm.get_test_area_retail`

### 5.3 use Inflation rate to get standard retail amount and mark_concern percentage

`algorithm.get_test_area_retail_inflation_correction`
`algorithm.get_test_area_markanteil_correction`


### 5.4 apply the 4 possibility to the retail amount

`algorithm.get_test_area_customer_shop_possibility`

**TBD**

### 5.5 Convert the payment to the quantity of goods(on prediction year)

need fund-volume relationship

**TBD**

## 6. consider changes within a year(seasonal difference and holiday influence)


`algorithm.get_test_area_retail_month_correction`

## 7. use map to find matching driving paths through shops

IS route planning a part of the job?
(use the shop coordinates and find one/multi way/ways through
all shops)

external api and server?

**VRP Problem/ local genetic algorithm**

**TBD**

`algorithm.VRP`

testcode `test.VRP_test_code`
