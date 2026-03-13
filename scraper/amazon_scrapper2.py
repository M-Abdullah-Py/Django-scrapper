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

# def fetch_html(url, query,save_path="page.html"):
    
#     chrome_options = Options()
#     chrome_options.add_argument("--headless=new") 
#     # chrome_options.add_argument("--start-maximized")
#     chrome_options.add_argument("--window-size=1920,1080")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
#     driver = webdriver.Chrome(options=chrome_options)
    
#     try:
#         driver.get(url)
        
#         # wait for JS to load
#         # time.sleep(10)

#         search_bar = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
#         )
        
#         search_bar.send_keys(query)
#         search_bar.send_keys(Keys.RETURN)

#         element = driver.find_element(By.XPATH, "//span[@data-component-type='s-search-results' and @class='rush-component s-latency-cf-section']")

#         html = element.get_attribute("outerHTML")

#         print(html)      
#         # Save HTML
#         with open(save_path, "w", encoding="utf-8") as f:
#             f.write(html)
        
#         print("HTML saved successfully!")
    
#     finally:
#         driver.quit()


import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# def fetch_html(url ,query, save_path="page.html"):
#     ua = UserAgent()
#     headers = {
#         'User-Agent': ua.random,
#         'Accept-Language': 'en-US,en;q=0.9',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#         'Referer': 'https://www.amazon.com/',
#     }
    
#     search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
    
#     response = requests.get(search_url, headers=headers, timeout=30)
    
#     with open(save_path, "w", encoding="utf-8") as f:
#         f.write(response.text)
    
#     print(f"HTML saved! Status: {response.status_code}")
#     # print(f"HTML saved! Status: {response.text}")


import time
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

def fetch_html(url, query, save_path="page.html"):
    session = requests.Session()

    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com/',
    }

    # Visit homepage first to get real cookies
    try:
        session.get("https://www.amazon.com/", headers=headers, timeout=15)
        time.sleep(random.uniform(1.5, 3.0))
    except Exception:
        pass

    search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
    response = session.get(search_url, headers=headers, timeout=30)

    blocked = (
        response.status_code != 200
        or "<title>Sorry" in response.text[:500]
        or "api-services-support@amazon.com" in response.text[:1000]
    )

    if blocked:
        print(f"❌ Blocked by Amazon (status={response.status_code}). Consider using ScraperAPI.")
        return False

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"✅ HTML saved! Status: {response.status_code}")
    return True

# fetch_html(query="laptops")
import re

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
            # reset price variables to avoid stale data
            price = None
            price_numeric = None
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
                # rating = review_element.select_one("div.a-row.a-size-small span").get_text()
                # rating_elem = product.select_one("div.a-row.a-size-small span")
                rating_elem = product.select_one("i[data-cy=reviews-ratings-slot] span")
                rating = rating_elem.get_text(strip=True) if rating_elem else None
                if rating and "out" in rating:
                    rating = rating.split(" ")[0]
                    print(rating)


                # total_ratings_block = product.select_one("span.rush-component[data-component-type='s-client-side-analytics'] span")
                # print(total_ratings_block)
                # total_ratings = total_ratings_block.get_text() if total_ratings_block else None   
                # if total_ratings:
                #     total_ratings = total_ratings.strip("()")
                #     print(total_ratings)
                anchor = review_element.find("a")
                ratings_match = re.search(r"\(([^)]+)\)", anchor.get_text(strip=True))
                total_ratings = ratings_match.group(1) if ratings_match else None
                print(total_ratings)
              
                
                
                rows = product.select("div.a-row")
                sold_elem = rows[-1].select_one("span.a-color-secondary")
                # sold_elem = review_element.select_one("div.a-row:nth-of-type(2) span.a-color-secondary")
                sold = sold_elem.text if sold_elem else None

            else:
                total_ratings = None
                rating = None
                sold = None
            price_element = product.select_one("div[data-cy='price-recipe']")
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
                    # import re
                    # clean_price = re.sub(r'[^\d.]', '', clean_price)
                    
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
                # 'sold': sold,
                'total_ratings':total_ratings,
                # 'price': price_numeric,  # Numeric for calculations
                'price_display': price_display,
                'Link':product_link  
            })
            
            print(f"Title: {clean_title[:50]}...")
            print(f"link: {product_link}")
            print(f"Rating: {rating}, Sold: {sold}, Total Ratings:{total_ratings}, Price: {price_numeric}, Price real:{price}")
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
    # query = "smartphones"
    query = input("Query: ")
    url = f"https://www.amazon.com/"
    
    # Uncomment to fetch fresh HTML
    fetch_html(url, query, f"{query.replace(" ", "_")}.html" )
    
    # Parse products
    Products = parse_products(f"{query.replace(" ", "_")}.html")
    print(f"\n✅ Total products scraped: {len(Products)}")
    
    # # Save to CSV using pandas
    # if Products:
    #     df = save_to_csv(Products, "amazon_laptops.csv")
        
    #     # Optional: Do some analysis
    #     print(f"\n📈 Price Statistics:")
    #     print(df['price_display'].describe())
    # else:
    #     print("❌ No products found to save!")