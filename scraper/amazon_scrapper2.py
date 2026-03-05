from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import pandas as pd 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_html(url, query,save_path="page.html"):
    
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        
        # wait for JS to load
        # time.sleep(10)

        search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        )
        
        search_bar.send_keys(query)
        search_bar.send_keys(Keys.RETURN)

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
        try:  # 👈 Add try-except for error handling
            title_elem = product.select_one("h2 span")
            if title_elem:
                clean_title = ' '.join(title_elem.text.split())
            else:
                clean_title = None
            
            parent_link = title_elem.find_parent("a")
            product_link = parent_link["href"]
            product_link = f"https://amazon.com{product_link}"
            
            review_element = product.select_one("div[data-cy='reviews-block']")
            if review_element:
                rating = review_element.select_one("div.a-row.a-size-small span").get_text()
                sold_elem = review_element.select_one("div.a-size-base")
                sold = sold_elem.text if sold_elem else None
            else:
                rating = None
                sold = None
            price_element = product.select_one("div.puisg-row")
            if price_element:
                price_elem = price_element.select_one("span.a-price > span.a-offscreen")
                if price_elem:
                    raw_price = price_elem.text
                    
                    # 🔥 IMPROVED PRICE CLEANING 🔥
                    # Detect currency symbol
                    currency_symbol = ''
                    if 'PKR' in raw_price or '₹' in raw_price or '£' in raw_price:
                        currency_symbol = 'PKR' if 'PKR' in raw_price else 'Other'
                    
                    # Clean the price
                    clean_price = raw_price.replace('PKR', '').replace('Â', '').replace('$', '').replace('₹', '').replace('£', '').replace(',', '').strip()
                    
                    # Remove any other non-numeric characters except decimal point
                    import re
                    clean_price = re.sub(r'[^\d.]', '', clean_price)
                    
                    # Convert to float
                    price = float(clean_price) if clean_price else None
                    
                    # Store both original and cleaned price
                    price_numeric = price
                    price_display = f"{price:,.2f}" if price else None  # Always show in USD for display
                    
                else:
                    price_numeric = None
                    price_display = None
            else:
                price_numeric = None
                price_display = None
            # price_element = product.select_one("div.puisg-row")
            # if price_element:
            #     price_elem = price_element.select_one("span.a-price > span.a-offscreen")
            #     if price_elem:
            #         raw_price = price_elem.text
            #         # # Price cleaning
            #         # Remove PKR, Â, commas, and extra spaces
            #         clean_price = raw_price.replace('PKR', '').replace('Â', '').replace(',', '').strip()
            #         # Remove any other non-numeric characters except decimal point
            #         import re
            #         clean_price = re.sub(r'[^\d.]', '', clean_price)
            #         price = float(clean_price) if clean_price else None
            #     else:
            #         price = None
            # else:
            #     price = None

            Products.append({
                'title': clean_title,
                'rating': rating,
                'sold': sold,
                'price': price_numeric,  # Numeric for calculations
                'price_display': price_display,
                'Link':product_link  
            })
            
            print(f"Title: {clean_title[:50]}...")
            print(f"link: {product_link}"),
            print(f"Rating: {rating}, Sold: {sold}, Price: {price}")
            print("-" * 30)
            
        except Exception as e:
            print(f"Error parsing product: {e}")
            continue

    return Products

def save_to_csv(products, filename="amazon_products.csv"):
    """
    Convert products list to DataFrame and save as CSV
    """
    # Create DataFrame
    df = pd.DataFrame(products)
    
    
    # Save to CSV
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"\n✅ Data saved to {filename}")
    
    # Display basic info
    print(f"\n📊 DataFrame Info:")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst 5 rows:")
    print(df.head())
    
    return df

if __name__ == "__main__":
    query = "laptops"
    url = f"https://www.amazon.com/"
    
    # Uncomment to fetch fresh HTML
    fetch_html(url, query, "amazon.html" )
    
    # Parse products
    Products = parse_products("amazon.html")
    print(f"\n✅ Total products scraped: {len(Products)}")
    
    # Save to CSV using pandas
    if Products:
        df = save_to_csv(Products, "amazon_laptops.csv")
        
        # Optional: Do some analysis
        print(f"\n📈 Price Statistics:")
        print(df['price'].describe())
    else:
        print("❌ No products found to save!")