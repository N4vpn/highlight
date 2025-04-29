import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import base64
from cryptography.fernet import Fernet
import os
import hashlib
from urllib.parse import urlparse, urlunparse, parse_qs

# Encryption Configuration
ENCRYPTION_PASSWORD = "the_reds_show"  # Change this to your secure password
BASE_URL = "https://tiksports.net"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Generate encryption key from password
def generate_key(password):
    # Hash the password to get consistent 32-byte key
    hashed = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

# Initialize encryption
KEY = generate_key(ENCRYPTION_PASSWORD)
CIPHER = Fernet(KEY)

def encrypt_data(data):
    """Encrypt JSON data using Fernet encryption"""
    json_str = json.dumps(data)
    encrypted_data = CIPHER.encrypt(json_str.encode())
    return encrypted_data

def fetch_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_highlights(match_url):
    html = fetch_page(match_url)
    if not html: return []
    soup = BeautifulSoup(html, 'html.parser')
    highlights = []
    server_div = soup.find('div', class_='list-server')
    if server_div:
        for btn in server_div.find_all('button', class_='btn-server'):
            if 'Highlight' in btn.text:
                highlights.append({
                    'name': btn.text.strip(),
                    'url': btn.get('data-link', '').strip(),
                })
    return highlights

def clean_logo_url(logo_url):
    """Remove query parameters from the logo URL."""
    if logo_url:
        parsed_url = urlparse(logo_url)
        parsed_url = parsed_url._replace(query='')  # Remove the query part
        return urlunparse(parsed_url)  # Return the cleaned URL
    return logo_url

def get_all_matches():
    try:
        html = fetch_page(f"{BASE_URL}/highlights.html")
        if not html: return []
        soup = BeautifulSoup(html, 'html.parser')
        matches = []
        for row in soup.find_all('div', class_='common-table-row table-row'):
            try:
                match_data = {
                    "time": row.find('span', class_='match-time').text if row.find('span', class_='match-time') else "N/A",
                    "league": row.find('a', class_='league-name').get('alt', 'N/A'),
                    "home_team": {
                        "name": row.find('div', class_='first-club').find('div', class_='club-name').text.strip(),
                        "logo": clean_logo_url(row.find('div', class_='first-club').find('img')['src']) if row.find('div', class_='first-club').find('img') else None,
                        "score": row.find('div', class_='first-club').find('span', class_='b-text-dark').text.strip() if row.find('div', class_='first-club').find('span', class_='b-text-dark') else None
                    },
                    "away_team": {
                        "name": row.find('div', class_='last-club').find('div', class_='club-name').text.strip(),
                        "logo": clean_logo_url(row.find('div', class_='last-club').find('img')['src']) if row.find('div', class_='last-club').find('img') else None,
                        "score": row.find('div', class_='last-club').find('span', class_='b-text-dark').text.strip() if row.find('div', class_='last-club').find('span', class_='b-text-dark') else None
                    }
                }
                match_url_tag = row.find('a', class_='right-row')
                if match_url_tag:
                    match_url = BASE_URL + match_url_tag['href']
                    match_data['video_link'] = extract_highlights(match_url)
                matches.append(match_data)
            except Exception as e:
                print(f"Skipping a match due to error: {e}")
        return matches
    except Exception as e:
        print(f"Scraping failed: {e}")
        return []

if __name__ == "__main__":
    # Get matches data
    matches = get_all_matches()
    
    # Save unencrypted version (optional)
    encrypted_data = encrypt_data(matches)
    with open('highlight.json', 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=4, ensure_ascii=False)
    # with open('highlight.json', 'wb') as f:
    #     f.write(encrypted_data)
