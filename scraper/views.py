from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import pandas as pd
from scraper.amazon_scrapper2 import fetch_html, parse_products  # Import your functions

def index(request):
    """Render the main page"""
    return render(request, 'scraper/index.html')

# @csrf_exempt
# def scrape_amazon(request):
#     """Handle scraping requests"""
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             query = data.get('query', 'laptops')
            
#             # Create a unique filename for CSV
#             import time
#             timestamp = int(time.time())
#             csv_filename = f'amazon_{query}_{timestamp}.csv'
#             csv_path = os.path.join(settings.MEDIA_ROOT, csv_filename)
            
#             # Run scraper
#             url = f"https://www.amazon.com/s?k={query}"
            
#             # Fetch HTML (uncomment if you want to fetch fresh)
#             fetch_html(url, "amazon.html")
            
#             # Parse products
#             products = parse_products("amazon.html")
            
#             if products:
#                 # Save to CSV
#                 df = pd.DataFrame(products)
#                 df.to_csv(csv_path, index=False)
                
#                 # Return data and CSV URL
#                 return JsonResponse({
#                     'success': True,
#                     'products': products[:10],  # First 10 for preview
#                     'total': len(products),
#                     'csv_url': f'/media/{csv_filename}',
#                     'message': f'Successfully scraped {len(products)} products'
#                 })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'No products found'
#                 })
                
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'message': str(e)
#             })
    
#     return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def scrape_amazon(request):
    """Handle scraping requests"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', 'laptops')
            
            # Create a unique filename for CSV
            import time
            timestamp = int(time.time())
            csv_filename = f'amazon_{query}_{timestamp}.csv'
            
            from django.conf import settings
            csv_path = os.path.join(settings.MEDIA_ROOT, csv_filename)
            
            print(f"Saving CSV to: {csv_path}")
            
            # Run scraper
            url = f"https://www.amazon.com/s?k={query}&crid=V2YUMNTD1KX6&sprefix={query}%2Caps%2C420&ref=nb_sb_noss_1"

            html_file_name = f'{query}_{timestamp}.html'
            html_path = os.path.join(settings.MEDIA_ROOT, html_file_name)

            fetch_html(url, html_path)
            # Parse products
            products = parse_products(html_path)
            
            if products:
                # Save to CSV
                df = pd.DataFrame(products)
                df.to_csv(csv_path, index=False)
                
                # Prepare products for display (use price_display)
                display_products = []
                for p in products[:10]:
                    display_products.append({
                        'title': p['title'],
                        'rating': p['rating'],
                        'sold': p['sold'],
                        'price': p['price_display'] or f"${p['price']:,.2f}" if p['price'] else 'N/A'
                    })
                
                return JsonResponse({
                    'success': True,
                    'products': display_products,
                    'total': len(products),
                    'csv_url': f'/media/{csv_filename}',
                    'message': f'Successfully scraped {len(products)} products'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No products found'
                })
                
        except Exception as e:
            print(f"Error in scrape_amazon: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})