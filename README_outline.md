# Workflow

## 1. parameters init

get all parameters ready

## 2. get involved shop information


### 2.1 get coordinates with the init shop name list

Normally, this step is not part of the project, because the coordinates
of the test shops should be offered before the program starts in a
.xlsx file.

Or the original file could only contain name and address of 
the shops. Under such circumstances, 2.1 is necessary.

#### 2.1.1 from Nominatim Server

Use the IMN's Nominatim server to search for the coordinates(fast).
However, some coordinates point on Nominatim can differ from those
in .osm.pbf files. So in this case, an offset of coordinates.(+-0.003)

`alternative_Nominativ.get_coordinate_from_Nominatim`


#### 2.1.2 from .pbf file

use the .osm.pbf file to search for the coordinates(slow)

due to (unkonwn)_**(really?)**_ coordinates of the shop, all
.pbf file needs to be searched.

`alternative_osm.get_coordinate_from_address`

##### _TBD_ 

The main functions already exist but still need to be 
adjusted to fit the main program's demand.

### 2.2 use the coordinates to get information about involved blocks

maximum longitude and latitude from shop list

`algorith.calc_test_area_info`

### 2.3 use the involved blocks' coordinates and extract the test area's osm file

`osm_object_Methods.osm_extract_from_pbf`

### 2.4 use the 2.2 blocks' geo coordinates to search for other involved shops' coordinates

blocks' coordinates from 2.2, +-0.0415?(half block side length)

`alternative_Nominatim.Nominatim_find_shops`


#### 2.4.1 from Nominatim Server

search for all shops' list in certain area

`alternative_Nominatim.Nominatim_find_shops`

#### 2.4.2 from .pbf file

use the 2.3 osm file to traverse and coordinates as bounding box

**TBD**

### 2.5 use the 2.1&2.4 coordinates to get shop information from .pbf file (area, facility, grade etc.)

from .osm.pbf, google grade into a .xlsx file
`osm_object_Methods`
`???`

**TBD**

## 3. calculate every shop attraction influence using attractiveness formula with shop information from 2.5

**TBD**

## 4. use Huff Method to calculate the possibility for population on each block to go to a specific shop

### 4.1 calculate the driving distance from each block to shop(pbf)

`osm_object_Methodes.get_route_distance`

### 4.2 analyse the relationship between different marks (Rewe-Lidi, Commodity substitution rate)

use wholesale amount / retail store number = avg(Brand_shop)
and take that shop information as default to compare with each
other.

**TBD**

## 5. get retail amount and cargo volume

### 5.1 use .csv file and data fitting to get average retail sale amount on prediction year for the chosen state

`algorithm.calc_retail_average`

### 5.2 get test district whole retail amount on prediction year(5.1*population on blocks)

`algorithm.calc_test_area_retail`

### 5.3 use Inflation rate to get standard retail amount

inflation rate csv/xlsx file?

retail / business proportion?

**TBD**
`algorithm.get_test_area_retail_inflation_correction`

### 5.4 apply the 4 possibility to the retail amount

**TBD**

### 5.5 Convert the payment to the quantity of goods(on prediction year)

need money-volumn relationship

**TBD**

## 6. consider changes within a year(seasonal difference and holiday influence)

**TBD**
