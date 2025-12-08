import os
from dotenv import load_dotenv
import googlemaps
import pandas as pd
import time
import numpy as np

load_dotenv()

gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

apartments_df = pd.read_csv('../data/apartments_v5.csv')
bus_stops_df = pd.read_csv('../data/bus_stops_v1.csv')

print(f"Found {len(apartments_df)} apartments and {len(bus_stops_df)} bus stops")
print(f"Total combinations to calculate: {len(apartments_df) * len(bus_stops_df)}\n")

apartment_ids = []
bus_stop_ids = []
distances_miles = []
times_min = []

# Prepare bus stop coordinates as (lat, lng) tuples for batch API calls
bus_stop_coordinates = [(row['Latitude'], row['Longitude']) for _, row in bus_stops_df.iterrows()]
bus_stop_id_list = bus_stops_df['Stop ID (Full)'].tolist()

# Google Maps Distance Matrix API limits:
# - MAX_DIMENSIONS_EXCEEDED: Maximum 25 destinations per request
# - MAX_ELEMENTS_EXCEEDED: Maximum 100 elements per request (1 origin × 25 destinations = 25 elements)
# Split bus stops into batches of 25 to avoid MAX_DIMENSIONS_EXCEEDED error
BATCH_SIZE = 25
num_batches = (len(bus_stops_df) + BATCH_SIZE - 1) // BATCH_SIZE

for idx, apartment_row in apartments_df.iterrows():
    apartment_id = apartment_row['id']
    apartment_name = apartment_row['name']
    apartment_address = apartment_row['address']
    
    print(f"Processing {idx + 1}/{len(apartments_df)}: {apartment_name}")
    
    # Process bus stops in batches
    for batch_num in range(num_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(bus_stops_df))
        
        batch_coordinates = bus_stop_coordinates[start_idx:end_idx]
        batch_ids = bus_stop_id_list[start_idx:end_idx]
        
        try:
            result = gmaps.distance_matrix(
                origins=apartment_address,
                destinations=batch_coordinates,
                mode="walking"
            )
            
            if result['status'] == 'OK':
                elements = result['rows'][0]['elements']
                
                for batch_idx, element in enumerate(elements):
                    bus_stop_id = batch_ids[batch_idx]
                    
                    if element['status'] == 'OK':
                        # Distance is in meters, convert to miles
                        distance_meters = element['distance']['value']
                        distance_miles = distance_meters / 1609.34
                        
                        # Duration is in seconds, convert to minutes
                        duration_seconds = element['duration']['value']
                        duration_min = duration_seconds / 60
                        
                        apartment_ids.append(apartment_id)
                        bus_stop_ids.append(bus_stop_id)
                        distances_miles.append(distance_miles)
                        times_min.append(duration_min)
                    else:
                        print(f"  Warning: Could not calculate route to bus stop {start_idx + batch_idx + 1} - {element['status']}")
                        apartment_ids.append(apartment_id)
                        bus_stop_ids.append(bus_stop_id)
                        distances_miles.append(np.nan)
                        times_min.append(np.nan)
            else:
                print(f"  Warning: API request failed for batch {batch_num + 1} - {result['status']}")
                for batch_idx in range(len(batch_ids)):
                    apartment_ids.append(apartment_id)
                    bus_stop_ids.append(batch_ids[batch_idx])
                    distances_miles.append(np.nan)
                    times_min.append(np.nan)
        
        except Exception as e:
            print(f"  Error in batch {batch_num + 1}: {str(e)}")
            for batch_idx in range(len(batch_ids)):
                apartment_ids.append(apartment_id)
                bus_stop_ids.append(batch_ids[batch_idx])
                distances_miles.append(np.nan)
                times_min.append(np.nan)
        
        time.sleep(0.5)
    time.sleep(0.5)

results_df = pd.DataFrame({
    'apartment_id': apartment_ids,
    'bus_stop_id': bus_stop_ids,
    'distance_miles': distances_miles,
    'time_min': times_min
})

output_path = '../data/bus_stop_distances.csv'
results_df.to_csv(output_path, index=False)

successful = results_df['distance_miles'].notna().sum()
failed = results_df['distance_miles'].isna().sum()

print(f"\nSummary:")
print(f"  Successful calculations: {successful}")
print(f"  Failed calculations: {failed}")
print(f"\nResults saved to {output_path}")

