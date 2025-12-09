import pandas as pd
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth using the haversine formula.
    Returns: Distance in miles
    """
    # Earth's radius in miles
    R = 3958.8
    
    # Convert latitude and longitude from degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in miles
    distance = R * c
    
    return distance

apartments_df = pd.read_csv('../data/apartments_v5.csv')
crimes_df = pd.read_csv('../data/crimes_v3.csv')

print(f"Found {len(apartments_df)} apartments and {len(crimes_df)} crimes")
print(f"Total combinations to calculate: {len(apartments_df) * len(crimes_df)}\n")

# Convert to numeric, coercing errors to NaN
apartments_df['lat'] = pd.to_numeric(apartments_df['lat'], errors='coerce')
apartments_df['lng'] = pd.to_numeric(apartments_df['lng'], errors='coerce')
crimes_df['lat'] = pd.to_numeric(crimes_df['lat'], errors='coerce')
crimes_df['lng'] = pd.to_numeric(crimes_df['lng'], errors='coerce')

apartment_ids = []
case_numbers = []
distances_miles = []

skipped_apartments = 0
skipped_crimes = set()

for apt_idx, apt_row in apartments_df.iterrows():
    apt_id = apt_row['id']
    apt_lat = apt_row['lat']
    apt_lng = apt_row['lng']
    
    # Skip if apartment coordinates are invalid
    if pd.isna(apt_lat) or pd.isna(apt_lng):
        skipped_apartments += 1
        print(f"Warning: Skipping apartment {apt_id} - invalid coordinates")
        continue
    
    for crime_idx, crime_row in crimes_df.iterrows():
        case_number = crime_row['Case Number']
        crime_lat = crime_row['lat']
        crime_lng = crime_row['lng']
        
        # Skip if crime coordinates are invalid
        if pd.isna(crime_lat) or pd.isna(crime_lng):
            if case_number not in skipped_crimes:
                skipped_crimes.add(case_number)
                print(f"Warning: Skipping crime {case_number} - invalid coordinates")
            continue
        
        distance = haversine_distance(apt_lat, apt_lng, crime_lat, crime_lng)
        
        apartment_ids.append(apt_id)
        case_numbers.append(case_number)
        distances_miles.append(distance)

results_df = pd.DataFrame({
    'apartment_id': apartment_ids,
    'case_number': case_numbers,
    'distance_miles': distances_miles
})

output_path = '../data/crime_distances.csv'
results_df.to_csv(output_path, index=False)

total_combinations = len(results_df)
print(f"\nSummary:")
print(f"  Apartments processed: {len(apartments_df)}")
print(f"  Crimes processed: {len(crimes_df)}")
if skipped_apartments > 0:
    print(f"  Skipped apartments (invalid coordinates): {skipped_apartments}")
if len(skipped_crimes) > 0:
    print(f"  Skipped crimes (invalid coordinates): {len(skipped_crimes)}")
print(f"\nResults saved to {output_path}")
