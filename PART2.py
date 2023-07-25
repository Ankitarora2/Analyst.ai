import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape_product_page(driver, url):
    driver.get(url)
    time.sleep(3)  # Can increase to avoid overload

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    product_data = {}

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

    # DESCRIPTION
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

    # MANUFACTURER
    manufacturer_element = soup.find('a', {'id': 'bylineInfo'})
    if manufacturer_element:
        product_data['Manufacturer'] = manufacturer_element.get_text(strip=True)
    else:
        product_data['Manufacturer'] = 'N/A'

    return product_data


def scrape_multiple_product_pages(product_urls):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    all_products_data = []
    total_pages = len(product_urls)
    for i, url in enumerate(product_urls, 1):
        print(f"Scraping page {i}/{total_pages}")
        product_data = scrape_product_page(driver, url)
        all_products_data.append(product_data)

    driver.quit()

    return all_products_data

# READ PART1 OUTPUT
df = pd.read_csv('scraped_data.csv')
df = df.dropna(subset=['Product URL'])

# MAIN FUNCTION  of PART2 (Scrapping)
scraped_product_data = scrape_multiple_product_pages(df['Product URL'].tolist())

# Combine both outputs
product_df = pd.DataFrame(scraped_product_data)
merged_df = pd.concat([df.reset_index(drop=True), product_df], axis=1)

# SAVE FINAL OUTPUT
merged_df.to_csv('scraped_data_with_details.csv', index=False)
