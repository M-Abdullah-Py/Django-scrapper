document.addEventListener('DOMContentLoaded', function() {
    // Initialize particles.js
    particlesJS.load('particles-js', '{% static "js/particles.json" %}', function() {
        console.log('Particles loaded');
    });
    
    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    const scrapeBtn = document.getElementById('scrapeBtn');
    const queryInput = document.getElementById('queryInput');
    const regionSelect = document.getElementById('regionSelect');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsCard = document.getElementById('resultsCard');
    const tableBody = document.getElementById('tableBody');
    const productCount = document.getElementById('productCount');
    const totalProducts = document.getElementById('totalProducts');
    const downloadBtn = document.getElementById('downloadBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    const scrapeTime = document.getElementById('scrapeTime');
    
    let currentCsvUrl = '';
    let startTime;
    
    // Popular suggestions click
    document.querySelectorAll('.suggestions a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            queryInput.value = this.textContent;
            scrapeBtn.click();
        });
    });
    
    // Scrape button click handler
    scrapeBtn.addEventListener('click', async function() {
        const query = queryInput.value.trim();
        const region = regionSelect.value;
        const platform = document.querySelector('.tab-btn.active')?.dataset.platform || 'amazon';
        
        if (!query) {
            showNotification('Please enter a search query', 'warning');
            return;
        }
        
        startTime = Date.now();
        
        // Show loading with animation
        loadingSpinner.classList.remove('d-none');
        loadingSpinner.classList.add('animate__fadeIn');
        resultsCard.classList.add('d-none');
        scrapeBtn.disabled = true;
        scrapeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Scraping...';
        
        try {
            const response = await fetch('/scrape/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    query: query,
                    platform: platform,
                    region: region
                })
            });
            
            const data = await response.json();
            
            const endTime = Date.now();
            const timeInSeconds = ((endTime - startTime) / 1000).toFixed(1);
            
            if (data.success) {
                displayProducts(data.products);
                productCount.textContent = `${data.total} products`;
                totalProducts.textContent = data.total;
                scrapeTime.textContent = `${timeInSeconds}s`;
                currentCsvUrl = data.csv_url;
                downloadBtn.href = currentCsvUrl;
                resultsCard.classList.remove('d-none');
                resultsCard.classList.add('animate__fadeInUp');
                
                showNotification(`Successfully scraped ${data.total} products!`, 'success');
            } else {
                showNotification('Error: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('An error occurred while scraping', 'error');
        } finally {
            // Hide loading
            loadingSpinner.classList.add('d-none');
            scrapeBtn.disabled = false;
            scrapeBtn.innerHTML = '<i class="bi bi-lightning-charge"></i><span>Scrape Now</span>';
        }
    });
    
    // Refresh button
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            if (queryInput.value.trim()) {
                scrapeBtn.click();
            }
        });
    }
    
    // Display products in table
    function displayProducts(products) {
        tableBody.innerHTML = '';
        
        products.forEach((product, index) => {
            const row = document.createElement('tr');
            row.style.animation = `fadeInUp 0.5s ease ${index * 0.1}s both`;
            
            // Format rating stars
            const ratingValue = parseFloat(product.rating) || 0;
            const stars = getStarRating(ratingValue);
            
            row.innerHTML = `
                <td><span class="fw-bold text-primary">#${index + 1}</span></td>
                <td>
                    <div class="product-title">
                        <span class="title-text">${product.title || 'N/A'}</span>
                        <small class="asin text-muted d-block mt-1">${product.asin || ''}</small>
                    </div>
                </td>
                <td>
                    <div class="rating-container">
                        <span class="badge bg-warning">
                            <i class="bi bi-star-fill"></i> ${product.rating || 'N/A'}
                        </span>
                        ${stars}
                    </div>
                </td>
                <td>
                    <span class="sold-info">
                        <i class="bi bi-cart-check text-success"></i>
                        ${product.sold || 'N/A'}
                    </span>
                </td>
                <td>
                    <strong class="price-tag">
                        ${product.price || 'N/A'}
                    </strong>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Update showing info
        document.getElementById('showingEnd').textContent = Math.min(10, products.length);
    }
    
    // Helper function for star ratings
    function getStarRating(rating) {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        let stars = '';
        for (let i = 0; i < 5; i++) {
            if (i < fullStars) {
                stars += '<i class="bi bi-star-fill text-warning small ms-1"></i>';
            } else if (i === fullStars && halfStar) {
                stars += '<i class="bi bi-star-half text-warning small ms-1"></i>';
            } else {
                stars += '<i class="bi bi-star text-warning small ms-1"></i>';
            }
        }
        return `<div class="star-rating">${stars}</div>`;
    }
    
    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} animate__animated animate__fadeInRight`;
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            </div>
            <div class="notification-content">
                <p>${message}</p>
            </div>
            <button class="notification-close">
                <i class="bi bi-x"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('animate__fadeOutRight');
            setTimeout(() => notification.remove(), 500);
        }, 3000);
        
        notification.querySelector('.notification-close').addEventListener('click', function() {
            notification.classList.add('animate__fadeOutRight');
            setTimeout(() => notification.remove(), 500);
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
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});