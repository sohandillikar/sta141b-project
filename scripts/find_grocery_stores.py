import os
from dotenv import load_dotenv
import googlemaps
import pandas as pd
import time

load_dotenv()

gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

# Davis center coordinates (approximate center of Davis)
davis_center = (38.5449, -121.7405)
radius = 9656  # ~6 miles in meters (covers all of Davis)

all_grocery_stores = []
seen_place_ids = set()
queries = [
    'grocery store',
    'supermarket',
    'grocery',
    'food market',
    'grocery store in Davis'
]

print("Searching for grocery stores...")

for query in queries:
    try:
        places_result = gmaps.places(
            query=f"{query} in Davis, CA",
            location=davis_center,
            radius=radius
        )
        
        results = places_result.get('results', [])
        print(f"Found {len(results)} results for '{query}'")
        
        for place in results:
            place_id = place.get('place_id')
            if place_id in seen_place_ids:
                continue
            seen_place_ids.add(place_id)
            grocery_info = {
                'name': place.get('name'),
                'address': place.get('formatted_address'),
                'lat': place['geometry']['location']['lat'],
                'lng': place['geometry']['location']['lng'],
                'place_id': place_id,
                'rating': place.get('rating'),
                'user_ratings_total': place.get('user_ratings_total'),
                'types': place.get('types', [])
            }

            all_grocery_stores.append(grocery_info)
        
        while 'next_page_token' in places_result:
            time.sleep(2)
            places_result = gmaps.places(
                page_token=places_result['next_page_token']
            )
            results = places_result.get('results', [])
            
            for place in results:
                place_id = place.get('place_id')
                if place_id not in seen_place_ids:
                    seen_place_ids.add(place_id)
                    grocery_info = {
                        'name': place.get('name'),
                        'address': place.get('formatted_address'),
                        'lat': place['geometry']['location']['lat'],
                        'lng': place['geometry']['location']['lng'],
                        'place_id': place_id,
                        'rating': place.get('rating'),
                        'user_ratings_total': place.get('user_ratings_total'),
                        'types': place.get('types', [])
                    }
                    all_grocery_stores.append(grocery_info)
        
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        continue

print(f"\nTotal unique grocery stores found: {len(all_grocery_stores)}")

df = pd.DataFrame(all_grocery_stores)

df = df[df['address'].str.contains('Davis', case=False, na=False)]
df = df.sort_values('name').reset_index(drop=True)

df.to_csv('../data/grocery_stores_v1.csv', index=False)

print(f"\nSaved {len(df)} grocery stores to ../data/grocery_stores_v1.csv")
print("\nFirst 10 grocery stores:")
print(df[['name', 'address', 'rating']].head(10))