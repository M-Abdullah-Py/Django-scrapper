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
# from scraper.python_Test import fetch_html  # Import your functions

from django.http import FileResponse

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
            
            # Clean up old CSV files regularly (optional)
            # cleanup_old_files(days_old=2)
            
            print(f"Saving CSV to: {csv_path}")
            
            # Run scraper
            url = f"https://www.amazon.com/"

            html_file_name = f'{query}_{timestamp}.html'
            # html_file_name = 'smartphones_1772680529.html'
            html_path = os.path.join(settings.MEDIA_ROOT, html_file_name)

            fetch_html(url, query, html_path)
            # Parse products
            products = parse_products(html_path)
            
            # delete temporary html file to save space
            try:
                if os.path.exists(html_path):
                    os.remove(html_path)
                    print(f"Removed temporary HTML: {html_path}")
            except Exception as ex:
                print(f"Failed to delete html file: {ex}")
            
            if products:
                # Save to CSV
                df = pd.DataFrame(products)
                df.to_csv(csv_path, index=False)
                
                # Prepare products for display (use price_display)
                # Send ALL products for frontend pagination
                display_products = []
                for p in products:
                    display_products.append({
                        'title': p['title'],
                        'rating': p['rating'],
                        'sold': p['sold'],
                        # treat 0 as valid price
                        'price': p.get('price_display') or (f"${p['price']:,.2f}" if p.get('price') is not None else 'N/A'),
                        'link': p.get('Link', '#')  # Include the product link
                    })
                
                # ✅ FIX: Return full URL with domain
                request_url = request.build_absolute_uri('/')[:-1]
                csv_full_url = f"{request_url}/media/{csv_filename}"
                
                

                return JsonResponse({
                    'success': True,
                    'products': display_products,
                    'total': len(products),
                    'csv_url': csv_full_url,  # Full URL with domain
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

def download_csv(request, filename):
    """Serve CSV file for download"""
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return JsonResponse({'error': 'File not found'}, status=404)