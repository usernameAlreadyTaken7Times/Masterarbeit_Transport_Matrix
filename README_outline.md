# Workflow

## 1. parameters init

get all parameters ready

## 2. get involved shop information

### 2.1 get coordinates with init shop name list

Normally, this step is not part of the project, because the coordinates
of the test shops should be offered before the program starts in a
.xlsx file. 

#### 2.1.1 from Nominativ Server

Use the IMN's Nominativ server to search for the coordinates(fast).
However, some coordinates point on Nominativ can differ from those
in .osm.pbf files. So in this case, an offset of coordinates.(+-0.003)

`alternative_Nominativ`
`???`

#### 2.1.2 from .pbf file

use the .osm.pbf file to search for the coordinates(slow)

`alternative_osm.get_coordinate_from_address`

### 2.2 use the coordinates to get information about involved blocks

maximum longitute and latitude from shop list

`algorith.calc_test_area_info`

### 2.3 use the 2.2 blocks' geo coordinates to search for other involved shops' coordinates

blocks' coordinates from 2.2, +-0.0415?(half block side length)

`alternative_Nominatim.Nominatim_find_shops`


#### 2.3.1 from Nominativ Server

search for all shop list in certain area

`alternative_Nominatim.Nominatim_find_shops`

#### 2.3.2 from .pbf file

traverse and coordinates as bounding box

### 2.4 use the 2.1&2.3 coordinates to get shop information from .pbf file (area, facility, grade etc.)

from .osm.pbf, google grade into a .xlsx file
`osm_object_Methods`
`???`

**TBD**

## 3. calculate every shop attraction influence using attractiveness formula with shop information from 2.4



## 4. use Huff Method to calculate the possibility for population on each block to go to a specific shop

### 4.1 calculate the driving distance from each block to shop(pbf)

### 4.2 analyse the relationship between different marks (Rewe-Lidi, Commodity substitution rate)


## 5. get retail amount and cargo volume

### 5.1 use .csv file and data fitting to get average retail sale amount on prediction year for the chosen state

`algorithm.calc_retail_average`

### 5.2 get test district whole retail amount on prediction year(5.1*population on blocks)

`algorithm.calc_test_area_retail`

### 5.3 use Inflation rate to get standard retail amount

inflation rate csv/xlsx file?


### 5.4 apply the 4 possibily to the retail amount



### 5.4 Convert the payment to the quantity of goods(on prediction year)


## 6. consider changes within a year(seasonal difference and holiday influence)


