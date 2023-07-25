import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to scrape data from a single product page
def scrape_product_page(driver, url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    product_data = {}

    # Find ASIN using specific pattern or element search
    asin_pattern = re.compile(r'ASIN:\s*([A-Z0-9]+)')
    asin_match = re.search(asin_pattern, str(soup))
    if asin_match:
        product_data['ASIN'] = asin_match.group(1)
    else:
        asin_element = soup.find('input', {'name': 'ASIN'})
        if asin_element:
            product_data['ASIN'] = asin_element.get('value')
        else:
            product_data['ASIN'] = 'N/A'

    # Find Product Description using specific pattern or element search
    product_desc_pattern = re.compile(r'Product Description[\s\S]*?<div[^>]*>(.*?)<\/div>', re.IGNORECASE)
    product_desc_match = re.search(product_desc_pattern, str(soup))
    if product_desc_match:
        product_data['Product Description'] = product_desc_match.group(1).strip()
    else:
        product_desc_element = soup.find('div', {'id': 'feature-bullets'})
        if product_desc_element:
            product_data['Product Description'] = product_desc_element.get_text(strip=True)
        else:
            product_data['Product Description'] = 'N/A'

    # Find Manufacturer using specific pattern or element search
    manufacturer_element = soup.find('a', {'id': 'bylineInfo'})
    if manufacturer_element:
        product_data['Manufacturer'] = manufacturer_element.get_text(strip=True)
    else:
        product_data['Manufacturer'] = 'N/A'

    return product_data

# Function to scrape data from multiple product pages
def scrape_multiple_product_pages(product_urls):
    options = Options()
    options.add_argument('--headless')  # Run Chrome in headless mode (without opening a browser window)
    driver = webdriver.Chrome(options=options)

    all_products_data = []
    total_pages = len(product_urls)
    for i, url in enumerate(product_urls, 1):
        print(f"Scraping page {i}/{total_pages}")
        product_data = scrape_product_page(driver, url)
        all_products_data.append(product_data)

    driver.quit()

    return all_products_data

# Read the product URLs from the CSV file obtained in Part 1
df = pd.read_csv('scraped_data.csv')

# Filter out any rows with missing Product URLs
df = df.dropna(subset=['Product URL'])

# Scrape data from the product pages
scraped_product_data = scrape_multiple_product_pages(df['Product URL'].tolist())

# Combine the scraped data with the existing DataFrame
product_df = pd.DataFrame(scraped_product_data)
merged_df = pd.concat([df.reset_index(drop=True), product_df], axis=1)

# Save the merged DataFrame to a CSV file
merged_df.to_csv('scraped_data_with_details.csv', index=False)
