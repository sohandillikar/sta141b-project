from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import pandas as pd
import time

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    return uc.Chrome(options=options, version_main=None)

def scrape_apartment_info(url, driver):
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                driver.delete_all_cookies()
            
            driver.get(url)
            time.sleep(3)
            
            page_title = driver.title.lower()
            page_source = driver.page_source.lower()
            if "access denied" in page_title or "access denied" in page_source or "blocked" in page_source:
                if attempt < max_retries - 1:
                    print(f"  Access denied (attempt {attempt + 1}/{max_retries}), retrying...")
                    time.sleep(5)
                    continue
                else:
                    print(f"  Access denied after {max_retries} attempts")
                    return None, None
            
            rent = None
            try:
                rent_label = driver.find_element(By.XPATH, "//p[@class='rentInfoLabel' and text()='Monthly Rent']")
                rent_detail = rent_label.find_element(By.XPATH, "./following-sibling::p[@class='rentInfoDetail']")
                rent = rent_detail.text.split('\n')[0].strip()
            except Exception:
                rent = None
            
            square_feet = None
            try:
                sqft_label = driver.find_element(By.XPATH, "//p[@class='rentInfoLabel' and text()='Square Feet']")
                sqft_detail = sqft_label.find_element(By.XPATH, "./following-sibling::p[@class='rentInfoDetail']")
                square_feet = sqft_detail.text.split('\n')[0].strip()
            except Exception:
                square_feet = None
            
            return rent, square_feet
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Error (attempt {attempt + 1}/{max_retries}): {str(e)}, retrying...")
                time.sleep(5)
                continue
            else:
                print(f"  Error after {max_retries} attempts: {str(e)}")
                return None, None
    
    return None, None

def parse_rent(rent_string):
    if not rent_string:
        return float('nan'), float('nan')
    try:
        cleaned = rent_string.replace('$', '').replace(',', '').strip()
        if '-' in cleaned:
            parts = cleaned.split('-')
            if len(parts) == 2:
                min_val = float(parts[0].strip())
                max_val = float(parts[1].strip())
                return min_val, max_val
        else:
            val = float(cleaned)
            return val, val
    except Exception:
        return float('nan'), float('nan')

def parse_square_feet(sqft_string):
    if not sqft_string:
        return float('nan'), float('nan')
    try:
        cleaned = sqft_string.replace('sq ft', '').replace(',', '').strip()
        if '-' in cleaned:
            parts = cleaned.split('-')
            if len(parts) == 2:
                min_val = float(parts[0].strip())
                max_val = float(parts[1].strip())
                return min_val, max_val
        else:
            val = float(cleaned.strip())
            return val, val
    except Exception:
        return float('nan'), float('nan')

df = pd.read_csv('../data/apartments_v2.csv')

df['rent_min'] = float('nan')
df['rent_max'] = float('nan')
df['sqft_min'] = float('nan')
df['sqft_max'] = float('nan')

apartments_with_urls = df[df['apartments_url'].notna() & (df['apartments_url'] != '')].copy()
total_with_urls = len(apartments_with_urls)
total_apartments = len(df)
skipped = total_apartments - total_with_urls

print(f"Total apartments: {total_apartments}")
print(f"Apartments with URLs: {total_with_urls}")
print(f"Will skip (no URL): {skipped}\n")

driver = create_driver()

success_count = 0
fail_count = 0

try:
    for apartment_num, (idx, row) in enumerate(apartments_with_urls.iterrows(), 1):
        apartment_name = row['name']
        url = row['apartments_url']
        
        print(f"Processing apartment {apartment_num}/{total_with_urls}: {apartment_name}")
        
        driver.delete_all_cookies()
        
        rent_string, sqft_string = scrape_apartment_info(url, driver)
        
        if rent_string is None and sqft_string is None:
            fail_count += 1
            print(f"  Failed to scrape data\n")
        else:
            rent_min, rent_max = parse_rent(rent_string)
            sqft_min, sqft_max = parse_square_feet(sqft_string)
            
            df.at[idx, 'rent_min'] = rent_min
            df.at[idx, 'rent_max'] = rent_max
            df.at[idx, 'sqft_min'] = sqft_min
            df.at[idx, 'sqft_max'] = sqft_max
            if rent_min and rent_max and sqft_min and sqft_max:
                df.at[idx, 'rent_per_sqft_avg'] = (rent_min + rent_max) / (sqft_min + sqft_max)
            else:
                df.at[idx, 'rent_per_sqft_avg'] = float('nan')
            
            if pd.notna(rent_min) or pd.notna(sqft_min):
                success_count += 1
                print(f"  Rent: {rent_string if rent_string else 'N/A'}, Sqft: {sqft_string if sqft_string else 'N/A'}\n")
            else:
                fail_count += 1
                print(f"  Could not parse values\n")
        
        df.to_csv('../data/apartments_v3.csv', index=False, quoting=1)
        print(f"  Progress saved ({apartment_num}/{total_with_urls} completed)\n")
        
        if apartment_num < total_with_urls:
            time.sleep(4)

finally:
    print("\nClosing browser driver...")
    driver.quit()
    print("Driver closed")

print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print(f"Successfully scraped: {success_count}")
print(f"Failed: {fail_count}")
print(f"Skipped (no URL): {skipped}")
print(f"Total processed: {total_with_urls}")

print("\nFinalizing ../data/apartments_v3.csv...")
df.to_csv('../data/apartments_v3.csv', index=False, quoting=1)
print("All data saved to ../data/apartments_v3.csv")
