import os
from dotenv import load_dotenv
import googlemaps
import pandas as pd
import time
import numpy as np

load_dotenv()

gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

# Destination: UC Davis Quad
ucd_destination = "250 W Quad, Davis, CA 95616"

df = pd.read_csv('../data/apartments_v4.csv')

# Initialize lists to store results
distances_miles = []
times_min = []

# Process each apartment
for idx, row in df.iterrows():
    apartment_name = row['name']
    apartment_address = row['address']
    
    print(f"Processing {idx + 1}/{len(df)}: {apartment_name}")
    
    try:
        # Call Distance Matrix API
        result = gmaps.distance_matrix(
            origins=apartment_address,
            destinations=ucd_destination,
            mode="driving"
        )
        
        # Extract distance and duration from response
        if result['status'] == 'OK':
            element = result['rows'][0]['elements'][0]
            
            if element['status'] == 'OK':
                # Distance is in meters, convert to miles
                distance_meters = element['distance']['value']
                distance_miles = distance_meters / 1609.34
                
                # Duration is in seconds, convert to minutes
                duration_seconds = element['duration']['value']
                duration_min = duration_seconds / 60
                
                distances_miles.append(distance_miles)
                times_min.append(duration_min)
                
                print(f"  Distance: {distance_miles:.2f} miles, Time: {duration_min:.2f} minutes")
            else:
                # API returned an error for this specific route
                print(f"  Warning: Could not calculate route - {element['status']}")
                distances_miles.append(np.nan)
                times_min.append(np.nan)
        else:
            # API request failed
            print(f"  Warning: API request failed - {result['status']}")
            distances_miles.append(np.nan)
            times_min.append(np.nan)
    
    except Exception as e:
        # Handle any other errors
        print(f"  Error: {str(e)}")
        distances_miles.append(np.nan)
        times_min.append(np.nan)
    
    # Add delay between API calls
    time.sleep(0.5)

# Add new columns to DataFrame
df['ucd_distance_miles'] = distances_miles
df['ucd_time_min'] = times_min

# Export to apartments_v5.csv
output_path = '../data/apartments_v5.csv'
df.to_csv(output_path, index=False)

# Print summary statistics
successful = df['ucd_distance_miles'].notna().sum()
failed = df['ucd_distance_miles'].isna().sum()

print(f"Summary:")
print(f"  Successful calculations: {successful}")
print(f"  Failed calculations: {failed}")
print(f"\nResults saved to {output_path}")