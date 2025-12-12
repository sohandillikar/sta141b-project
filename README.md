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

- All scripts are in `scripts/`
- All datasets are in `data/`

### Apartments

#### Step 1: Getting a list of all apartment complexes in Davis

To get a list of all the apartment complexes and their ratings in Davis, we wrote a script called `find_apartments.py` that uses the Google Maps API to find all apartment complexes within a 6 mile radius of the center of Davis. We exported 81 apartments to `apartments_v1.csv`.

#### Step 2: Entering their apartments.com page URL

In order to extract information like monthly rent and square feet, we needed to use an API or build a scraper. Since all the APIs we looked at were paid or for enterprise use only, we were left with the option of scraping apartments.com. To do this, we manually entered the apartments.com page url for each complex in `apartments_v2.csv`.

#### Step 3: Scraping apartments.com

We built a scraper in `scrape_apartment_info.py` that scrapes the (`rent_min`, `rent_max`, `sqft_min`, `sqft_max`) for all the apartments in `apartments_v2.csv`, calculates the `rent_per_sqft_avg`, and exports them in `apartments_v3.csv`.

#### Step 4: Cleaning the apartments dataset

We removed apartments that did not have any of the following values since it would tamper with our algorithm: `rent_min`, `rent_max`, `sqft_min`, `sqft_max`. This version of the dataset was saved in `apartments_v4.csv`.

#### Step 5: Calculating distance from UC Davis

We calculated the driving distance in miles and minutes between the apartment complexes and Memorial Union by writing `ucd_distance.py` that uses the Distance Matrix function from the Google Maps API. We saved this data in `apartments_v5.csv`.

#### Step 6: Calculating distance from grocery stores

We calculated the driving distance in miles and minutes between each apartment complex and grocery store in `grocery_distance.py`, similar to `ucd_distance.py`. This time we used batching to limit the number of API calls and improve performance.

#### Step 7: Calculating distance from bus stops

We calculated the walking distance in miles and minutes between each apartment complex and bus stop in `bus_distance.py`, similar to `grocery_distance.py`. This time we used a different batching technique to avoid hitting the API call limits.

#### Step 8: Calculating distance from crimes

We calculated the straight-line distance in miles between each apartment and crime in `crime_distance.py`, using the Haversine Distance formula that accounts for Earth's curvature when calculating the distance between two coordinates.

### Grocery Stores

#### Step 1: Getting a list of all grocery stores in Davis

To get a list of all the grocery stores in Davis, we wrote a script called `find_grocery_stores.py` that uses the Google Maps API to find all grocery stores within a 6 mile radius of the center of Davis. We exported 68 grocery stores to `grocery_stores_v1.csv`.

#### Step 2: Filtering grocery stores

The earlier list in `grocery_stores_v1.csv` contained a list of grocery stores, cafes, liquor stores, home goods stores, etc., so we wrote a script in `filter_grocery_stores.ipynb` to filter out places that were not grocery stores. Then we exported the final list to `grocery_stores_v2.csv`.

### Bus Stops

#### Step 1: Converting a PDF to CSV

We found a list of all the bus stops and their addresses in [Unitrans Bus Stops Dataset](https://unitrans.ucdavis.edu/sites/g/files/dgvnsk13431/files/inline-files/BusStopAccessibilityList_20240909_StopID.pdf), then used Claude to convert the tables in the PDF into a CSV file which we saved in `bus_stops_v1.csv`.

### Crime Logs

#### Step 1: Converting a PDF to CSV

We found a list of the most recent Davis crimes and their addresses in [Davis Crimes Log](https://ucdavis.app.box.com/v/daily-police-logs/file/1894348886020), then prompted Claude to convert the tables in the PDF into a CSV file which we saved in `crimes_v1.csv`.

#### Step 2: Filtering and mapping crime severities

We wrote a script in `crime_severity_mapping.py` that removed non-Davis crimes (case numbers that did not start with 'C') and mapped each crime to a severity level on a scale of 1 to 10. We saved this new dataset to `crimes_v2.csv`.

#### Step 3: Geocoding all crimes

In `crime_geocoding.py`, we geocoded all the crimes street addresses to retrieve their latitude and longitude coordinates. We exported this data to `crimes_v3.csv`.

---

## Apartment Ranking Methodology

To create a ranking system of the apartment complexes, we developed a composite scoring system that combines multiple factors into a single quantitative measure. This system normalizes different metrics into a common scale and applies weighted importance to each factor.

### Normalization Process

All metrics are normalized to a 0-1 scale using min-max normalization. The normalization formula is:

```
normalized_value = (value - min) / (max - min)
```

For factors where lower values are preferable (such as distance or crime counts), we apply reverse normalization:

```
normalized_value = 1 - (value - min) / (max - min)
```

A score closer to 1 represents a better outcome.

### Individual Factor Scores

Five distinct factor scores are calculated for each apartment:

1. **Affordability Score**: Based on the average rent per square foot (`rent_per_sqft_avg`).

2. **Location Score**: Based on the driving distance to UC Davis (`ucd_distance_miles`).

3. **Accessibility Score**: Calculated as the average of two sub-scores:

   - **Grocery Score**: Based on distance to the nearest grocery store (`nearest_grocery_distance`), with reverse normalization
   - **Transit Score**: Based on distance to the nearest bus stop (`nearest_bus_stop_distance`), with reverse normalization

   This composite accessibility metric reflects convenience for daily living needs and public transportation access.

4. **Safety Score**: Based on the number of crimes reported within 0.5 miles of the apartment (`crimes_within_0.5mi`).

5. **Quality Score**: Based on the apartment's rating from reviews (`rating`).

### Composite Score Calculation

The overall composite score is calculated as a weighted linear combination of the five factor scores:

```
composite_score = 0.30 × affordability_score + 0.25 × location_score + 0.20 × accessibility_score + 0.15 × safety_score + 0.10 × quality_score
```

The weights reflect the relative importance of each factor for student housing decisions:

- **Affordability (30%)**: Highest weight, recognizing budget constraints for students
- **Location (25%)**: Second highest, emphasizing proximity to campus
- **Accessibility (20%)**: Important for daily convenience
- **Safety (15%)**: Significant but secondary to cost and location
- **Quality (10%)**: Lowest weight, as ratings may be less reliable or available
