import os
from dotenv import load_dotenv
import googlemaps
import pandas as pd
import time
import numpy as np

load_dotenv()

gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

df = pd.read_csv('../data/crimes_v2.csv')

initial_count = len(df)
invalid_location_count = 0
invalid_classification_count = 0
geocoding_failed_count = 0

# Filter rows with invalid Location
location_mask = (
    df['Location'].notna() & 
    (df['Location'].str.strip() != '') &
    (df['Location'].str.upper() != 'UNKNOWN') &
    (df['Location'].str.upper() != 'CASE NUMBER PULLED IN ERROR')
)

invalid_location_count = (~location_mask).sum()
df = df[location_mask].copy()

print(f"Removed {invalid_location_count} rows with invalid Location")

# Filter rows with invalid Classification
classification_mask = (
    df['Report Classification'].notna() &
    (df['Report Classification'].str.strip().str.upper() != 'UNKNOWN')
)

invalid_classification_count = (~classification_mask).sum()
df = df[classification_mask].copy()

print(f"Removed {invalid_classification_count} rows with invalid Classification")
print(f"Remaining rows to geocode: {len(df)}\n")

df['lat'] = np.nan
df['lng'] = np.nan

rows_to_remove = []

for idx, row in df.iterrows():
    location = row['Location']
    case_number = row['Case Number']
    
    formatted_address = f"{location}, Davis, CA"
    
    print(f"Geocoding {idx + 1}/{len(df)}: {location} (Case: {case_number})")
    
    try:
        geocode_result = gmaps.geocode(formatted_address)
        
        if geocode_result and len(geocode_result) > 0:
            location_data = geocode_result[0]['geometry']['location']
            df.at[idx, 'lat'] = location_data['lat']
            df.at[idx, 'lng'] = location_data['lng']
            print(f"  Success: ({location_data['lat']}, {location_data['lng']})")
        else:
            print(f"  Warning: No geocoding results found")
            rows_to_remove.append(idx)
            geocoding_failed_count += 1
    
    except Exception as e:
        print(f"  Error: {str(e)}")
        rows_to_remove.append(idx)
        geocoding_failed_count += 1
    
    # Add delay between API calls
    time.sleep(0.5)

# Remove rows where geocoding failed
if rows_to_remove:
    df = df.drop(index=rows_to_remove).copy()
    print(f"\nRemoved {len(rows_to_remove)} rows where geocoding failed")

# Save to new CSV file
output_path = '../data/crimes_v3.csv'
df.to_csv(output_path, index=False)

print(f"Summary:")
print(f"  Initial rows: {initial_count}")
print(f"  Removed (invalid Location): {invalid_location_count}")
print(f"  Removed (invalid Classification): {invalid_classification_count}")
print(f"  Removed (geocoding failed): {geocoding_failed_count}")
print(f"  Final rows: {len(df)}")
print(f"\nResults saved to {output_path}")

