import os
from dotenv import load_dotenv
import googlemaps
import pandas as pd
import time

load_dotenv()

# Initialize client
gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

# Davis center coordinates (approximate center of Davis)
davis_center = (38.5449, -121.7405)
radius = 9656  # ~6 miles in meters (covers all of Davis)

# List to store all results
all_apartments = []
seen_place_ids = set()

# Different search queries to catch various apartment types
queries = [
    'apartment complex',
    'apartment building', 
    'apartments',
    'student housing',
    'apartment community',
    'apartment rental'
]

print("Searching for apartments...")

for query in queries:
    try:
        # Search for places
        places_result = gmaps.places(
            query=f"{query} in Davis, CA",
            location=davis_center,
            radius=radius
        )
        
        results = places_result.get('results', [])
        print(f"Found {len(results)} results for '{query}'")
        
        # Process each result
        for place in results:
            place_id = place.get('place_id')
            
            # Skip duplicates
            if place_id in seen_place_ids:
                continue
            seen_place_ids.add(place_id)
            
            # Extract relevant information
            apartment_info = {
                'name': place.get('name'),
                'address': place.get('formatted_address'),
                'lat': place['geometry']['location']['lat'],
                'lng': place['geometry']['location']['lng'],
                'place_id': place_id,
                'rating': place.get('rating'),
                'user_ratings_total': place.get('user_ratings_total'),
                'types': place.get('types', [])
            }
            
            all_apartments.append(apartment_info)
        
        # Handle pagination if there's a next_page_token
        while 'next_page_token' in places_result:
            time.sleep(2)  # Required delay before using next_page_token
            places_result = gmaps.places(
                page_token=places_result['next_page_token']
            )
            results = places_result.get('results', [])
            
            for place in results:
                place_id = place.get('place_id')
                if place_id not in seen_place_ids:
                    seen_place_ids.add(place_id)
                    apartment_info = {
                        'name': place.get('name'),
                        'address': place.get('formatted_address'),
                        'lat': place['geometry']['location']['lat'],
                        'lng': place['geometry']['location']['lng'],
                        'place_id': place_id,
                        'rating': place.get('rating'),
                        'user_ratings_total': place.get('user_ratings_total'),
                        'types': place.get('types', [])
                    }
                    all_apartments.append(apartment_info)
        
        # Rate limiting - be nice to the API
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        continue

print(f"\nTotal unique apartments found: {len(all_apartments)}")

# Convert to DataFrame
df = pd.DataFrame(all_apartments)

# Filter to only Davis addresses
df = df[df['address'].str.contains('Davis', case=False, na=False)]

# Sort by name
df = df.sort_values('name').reset_index(drop=True)

# Save to CSV
df.to_csv('../data/apartments_v1.csv', index=False)
print(f"\nSaved {len(df)} apartments to ../data/apartments_v1.csv")

# Display first few results
print("\nFirst 10 apartments:")
print(df[['name', 'address', 'rating']].head(10))