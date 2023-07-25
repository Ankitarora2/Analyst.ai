from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape_page(driver, url):
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    products = []
    for product in soup.find_all('div', {'data-component-type': 's-search-result'}):
        product_data = {}
        product_data['Product URL'] = 'https://www.amazon.in' + product.find('a', {'class': 'a-link-normal'})['href']
        product_data['Product Name'] = product.find('span', {'class': 'a-size-medium'}).text.strip()
        price_element = product.find('span', {'class': 'a-price'})
        if price_element:
            price = price_element.find('span', {'class': 'a-offscreen'})
            if price:
                product_data['Product Price'] = price.text.replace('â‚¹', '').replace(',', '').strip()
            else:
                product_data['Product Price'] = 'N/A'
        else:
            product_data['Product Price'] = 'N/A'
        rating = product.find('span', {'class': 'a-icon-alt'})
        if rating:
            product_data['Rating'] = rating.text.split()[0]
        else:
            product_data['Rating'] = 'N/A'
        reviews = product.find('span', {'class': 'a-size-base'})
        if reviews:
            product_data['Number of reviews'] = reviews.text.replace(',', '')
        else:
            product_data['Number of reviews'] = 'N/A'

        products.append(product_data)

    return products


def scrape_multiple_pages(base_url, num_pages):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    all_products = []
    for page in range(1, num_pages + 1):
        url = base_url + f'&page={page}'
        print(f"Scraping Page No.{page}")
        products = scrape_page(driver, url)
        all_products.extend(products)

    driver.quit()

    return all_products


# URL, Number of pages (AS REQUIRED)
base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1'
num_pages_to_scrape = 20
scraped_data = scrape_multiple_pages(base_url, num_pages_to_scrape)

# Save the Data
df = pd.DataFrame(scraped_data)
df.to_csv('scraped_data.csv', index=False)
print(f"Saved to scraped_data.csv")
