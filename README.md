# STA 141B Project

**Goal:** Find the best student apartment complex in Davis based on the following:

| Criteria                         | Data Source                                                                                                                                          |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Monthly Rent per Sq Ft           | [Apartments.com](https://www.apartments.com)                                                                                                         |
| Distance from UC Davis           | Google Maps API                                                                                                                                      |
| Distance from a grocery store    | Google Maps API                                                                                                                                      |
| Distance from a bus line         | [Unitrans Bus Stops Dataset](https://unitrans.ucdavis.edu/sites/g/files/dgvnsk13431/files/inline-files/BusStopAccessibilityList_20240909_StopID.pdf) |
| Number of crimes within the area | [Davis Crimes Log](https://ucdavis.app.box.com/v/daily-police-logs/file/1894348886020)                                                               |
| Reviews of the apartment complex | Google Maps API                                                                                                                                      |

## Data Fetching, Cleaning, & Preprocessing

### Apartments

#### Step 1: Getting a list of all apartment complexes in Davis

To get a list of all the apartment complexes and their ratings in Davis, we wrote a script called `scripts/find_apartments.py` that uses the Google Maps API to find all apartment complexes within a 6 mile radius of the center of Davis. We exported 81 apartments to `data/apartments_v1.csv`.

#### Step 2: Entering their apartments.com page URL

In order to extract information like monthly rent and square feet, we needed to use an API or build a scraper. Since all the APIs we looked at were paid or for enterprise use only, we were left with the option of scraping apartments.com. To do this, we manually entered the apartments.com page url for each complex in `data/apartments_v2.csv`.

#### Step 3: Scraping apartments.com

We built a scraper in `scripts/scrape_apartment_info.py` that scrapes the (`rent_min`, `rent_max`, `sqft_min`, `sqft_max`) for all the apartments in `data/apartments_v2.csv` and exports them in `data/apartments_v3.csv`.

#### Step 4: Cleaning the apartments dataset

We removed apartments that did not have any of the following values since it would tamper with our algorithm: `rent_min`, `rent_max`, `sqft_min`, `sqft_max`. This version of the dataset was saved in `data/apartments_v4.csv`.

### Grocery Stores

#### Step 1: Getting a list of all grocery stores in Davis

To get a list of all the grocery stores in Davis, we wrote a script called `scripts/find_grocery_stores.py` that uses the Google Maps API to find all grocery stores within a 6 mile radius of the center of Davis. We exported 68 grocery stores to `data/grocery_stores_v1.csv`.

#### Step 2: Filtering grocery stores

The earlier list in `data/grocery_stores_v1.csv` contained a list of grocery stores, cafes, liquor stores, home goods stores, etc., so we wrote a script in `scripts/filter_grocery_stores.ipynb` to filter out places that were not grocery stores. Then we exported the final list to `data/grocery_stores_v2.csv`.

### Bus Stops

#### Step 1: Converting a PDF to CSV

We found a list of all the bus stops and their addresses in [Unitrans Bus Stops Dataset](https://unitrans.ucdavis.edu/sites/g/files/dgvnsk13431/files/inline-files/BusStopAccessibilityList_20240909_StopID.pdf), then used Claude to convert the tables in the PDF into a CSV file which we saved in `data/bus_stops_v1.csv`.

### Crime Logs

#### Step 1: Converting a PDF to CSV

We found a list of the most recent Davis crimes and their addresses in [Davis Crimes Log](https://ucdavis.app.box.com/v/daily-police-logs/file/1894348886020), then prompted Claude to convert the tables in the PDF into a CSV file which we saved in `data/crimes_v1.csv`.

#### Step 2: Filtering and mapping crime severities

We wrote a script in `scripts/crime_severity_mapping.py` that removed non-Davis crimes (case numbers that did not start with 'C') and mapped each crime to a severity level on a scale of 1 to 10. We saved this new dataset to `crimes_v2.csv`.
