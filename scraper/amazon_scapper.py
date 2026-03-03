from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import pandas as pd

def fetch_html(url, save_path="page.html"):
    
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        
        # wait for JS to load
        time.sleep(5)

        element = driver.find_element(By.XPATH, "//span[@data-component-type='s-search-results' and @class='rush-component s-latency-cf-section']")

        html = element.get_attribute("outerHTML")

        print(html)      
        # Save HTML
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        print("HTML saved successfully!")
    
    finally:
        driver.quit()


def parse_products(html_file="amazon.html"):
        
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Find all product containers
    product_containers = soup.select("div.s-result-item.s-asin[role='listitem']")
    print(f"Found {len(product_containers)} product containers.")

    Products = []

    for product in product_containers:
        title_elem = product.select_one("h2 span")
        if title_elem:
            clean_title = ' '.join(title_elem.text.split())
            print(clean_title)
        
        review_element = product.select_one("div[data-cy='reviews-block']")
        rating=review_element.select_one("div.a-row.a-size-small span" ).get_text()
        sold=review_element.select_one("div.a-size-base")
        print(sold.text)

        price_element = product.select_one("div.puisg-row")
        price = price_element.select_one("span.a-price > span").text
        price = price[4:]
        print(price)

        Products.append({
        'title': clean_title,
        'rating': rating,
        'sold': sold.text if sold else None,
        'price': price
    })
    print("-" * 50)  # Separator
    return Products


def save_to_csv(products, filename="amazon_products.csv"):
    """
    Convert products list to DataFrame and save as CSV
    """
    # Create DataFrame
    df = pd.DataFrame(products)
    
    # Basic cleaning
    df['price'] = pd.to_numeric(df['price'], errors='coerce')  # Convert price to numeric
    
    # Save to CSV
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"\n✅ Data saved to {filename}")

    return df 

if __name__ == "__main__":
    query = "laptops"
    url = f"https://www.amazon.com/s?k={query}"
    # fetch_html(url, "amazon.html")
    
    # Parse and display products
    Products = parse_products("amazon.html")

    if Products:
        df = save_to_csv(Products, "amazon_laptops.csv")
    print(f"Total products: {len(Products)}")
    for p in Products[:2]:
        print(p)


    