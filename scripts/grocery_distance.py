import os
from dotenv import load_dotenv
import googlemaps
import pandas as pd
import time
import numpy as np

load_dotenv()

gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

apartments_df = pd.read_csv('../data/apartments_v5.csv')
grocery_stores_df = pd.read_csv('../data/grocery_stores_v2.csv')

print(f"Found {len(apartments_df)} apartments and {len(grocery_stores_df)} grocery stores")
print(f"Total combinations to calculate: {len(apartments_df) * len(grocery_stores_df)}\n")

apartment_ids = []
grocery_store_ids = []
distances_miles = []
times_min = []

# Get all grocery store addresses for batch API calls
grocery_addresses = grocery_stores_df['address'].tolist()

for idx, apartment_row in apartments_df.iterrows():
    apartment_id = apartment_row['id']
    apartment_name = apartment_row['name']
    apartment_address = apartment_row['address']
    
    print(f"Processing {idx + 1}/{len(apartments_df)}: {apartment_name}")
    
    try:
        result = gmaps.distance_matrix(
            origins=apartment_address,
            destinations=grocery_addresses,
            mode="driving"
        )
        
        if result['status'] == 'OK':
            elements = result['rows'][0]['elements']
            
            for grocery_idx, element in enumerate(elements):
                grocery_store_id = grocery_stores_df.iloc[grocery_idx]['id']
                
                if element['status'] == 'OK':
                    # Distance is in meters, convert to miles
                    distance_meters = element['distance']['value']
                    distance_miles = distance_meters / 1609.34
                    
                    # Duration is in seconds, convert to minutes
                    duration_seconds = element['duration']['value']
                    duration_min = duration_seconds / 60
                    
                    apartment_ids.append(apartment_id)
                    grocery_store_ids.append(grocery_store_id)
                    distances_miles.append(distance_miles)
                    times_min.append(duration_min)
                else:
                    # API returned an error for this specific route
                    print(f"  Warning: Could not calculate route to grocery store {grocery_idx + 1} - {element['status']}")
                    apartment_ids.append(apartment_id)
                    grocery_store_ids.append(grocery_store_id)
                    distances_miles.append(np.nan)
                    times_min.append(np.nan)
        else:
            print(f"  Warning: API request failed - {result['status']}")
            for grocery_idx in range(len(grocery_stores_df)):
                apartment_ids.append(apartment_id)
                grocery_store_ids.append(grocery_stores_df.iloc[grocery_idx]['id'])
                distances_miles.append(np.nan)
                times_min.append(np.nan)
    
    except Exception as e:
        print(f"  Error: {str(e)}")
        # Add NaN values for all grocery stores for this apartment
        for grocery_idx in range(len(grocery_stores_df)):
            apartment_ids.append(apartment_id)
            grocery_store_ids.append(grocery_stores_df.iloc[grocery_idx]['id'])
            distances_miles.append(np.nan)
            times_min.append(np.nan)
    
    # Add delay between API calls
    if idx < len(apartments_df) - 1:
        time.sleep(0.5)

# Create DataFrame with results
results_df = pd.DataFrame({
    'apartment_id': apartment_ids,
    'grocery_store_id': grocery_store_ids,
    'distance_miles': distances_miles,
    'time_min': times_min
})

output_path = '../data/grocery_store_distances.csv'
results_df.to_csv(output_path, index=False)

total_combinations = len(results_df)
successful = results_df['distance_miles'].notna().sum()
failed = results_df['distance_miles'].isna().sum()

print(f"\nSummary:")
print(f"  Total combinations: {total_combinations}")
print(f"  Successful calculations: {successful}")
print(f"  Failed calculations: {failed}")
print(f"\nResults saved to {output_path}")