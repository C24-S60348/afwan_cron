from flask import Blueprint, render_template_string
import requests
import time
import threading

cachegeturl_bp = Blueprint('cachegeturl', __name__)

# Lock for thread-safe operations
cache_lock = threading.Lock()

# Initialize cache
cache = {
    'content': None,  # Store the page content
    'timestamp': None  # Store the time when the content was cached
}

def get_page(url, cache_duration=600):  # Cache duration set for up to 10 minutes
    current_time = time.time()
    with cache_lock:  # Ensure thread safety
        # Check if we have a cached version and it's still valid
        if cache['content'] is not None and (current_time - cache['timestamp'] < cache_duration):
            print("Returning cached content.")
            return cache['content']

    # Cache is missing or expired, fetch from the web
    response = requests.get(url)
    if response.status_code == 200:
        with cache_lock:  # Ensure thread safety when updating cache
            cache['content'] = response.text
            cache['timestamp'] = current_time
        print("Fetched new content and updated the cache.")
        return cache['content']
    else:
        print(f"Failed to fetch content. Status code: {response.status_code}")
        return None

@cachegeturl_bp.route('/cachegeturl', methods=['GET', 'POST'])
def cachegeturl_main():
    # Example usage
    url = 'https://www.google.com'
    page_content = get_page(url) 
    return render_template_string(page_content)