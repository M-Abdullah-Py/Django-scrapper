document.addEventListener('DOMContentLoaded', function() {
    const scrapeBtn = document.getElementById('scrapeBtn');
    const queryInput = document.getElementById('queryInput');
    const platformSelect = document.getElementById('platformSelect');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsCard = document.getElementById('resultsCard');
    const tableBody = document.getElementById('tableBody');
    const productCount = document.getElementById('productCount');
    const downloadBtn = document.getElementById('downloadBtn');
    
    let currentCsvUrl = '';
    
    // Scrape button click handler
    scrapeBtn.addEventListener('click', async function() {
        const query = queryInput.value.trim();
        const platform = platformSelect.value;
        
        if (!query) {
            alert('Please enter a search query');
            return;
        }
        
        // Show loading
        loadingSpinner.classList.remove('d-none');
        resultsCard.classList.add('d-none');
        scrapeBtn.disabled = true;
        
        try {
            const response = await fetch('/scrape/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    query: query,
                    platform: platform
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                displayProducts(data.products);
                productCount.textContent = `${data.total} products found`;
                currentCsvUrl = data.csv_url;
                downloadBtn.href = currentCsvUrl;
                resultsCard.classList.remove('d-none');
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while scraping');
        } finally {
            // Hide loading
            loadingSpinner.classList.add('d-none');
            scrapeBtn.disabled = false;
        }
    });
    
    // Display products in table
    function displayProducts(products) {
        tableBody.innerHTML = '';
        
        products.forEach((product, index) => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${product.title || 'N/A'}</td>
                <td>
                    <span class="badge bg-warning text-dark">
                        <i class="bi bi-star-fill"></i> ${product.rating || 'N/A'}
                    </span>
                </td>
                <td>${product.sold || 'N/A'}</td>
                <td><strong>${product.price || 'N/A'}</strong></td>
            `;
            
            tableBody.appendChild(row);
        });
    }
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Enter key press handler
    queryInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            scrapeBtn.click();
        }
    });
});