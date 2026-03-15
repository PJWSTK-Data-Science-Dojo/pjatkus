import requests
from bs4 import BeautifulSoup
import trafilatura
import json
import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_URLS_FILE = "urls.txt" 
OUTPUT_JSONL = "pjatk_data.jsonl"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
DELAY = 1  
MAX_WORKERS = 3 
timestamp = 1609459200 # 2026-01-01 00:00:00
local_time = time.localtime(timestamp)


def extract_main_text(html, url):

    text = trafilatura.extract(html, url=url, favor_precision=True)
    if text and len(text) > 200:  
        return text.strip()


    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        tag.decompose()
    
    main = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
    if main:
        text = main.get_text(separator='\n', strip=True)
    else:
        
        text = soup.body.get_text(separator='\n', strip=True) if soup.body else ""
    
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return '\n'.join(lines)


def process_url(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8'
        if resp.status_code != 200:
            return None

        
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else ""

       
        text = extract_main_text(resp.text, url)
        if not text or len(text) < 100:  
            return None

        return {
            "url": url,
            "title": title,
            "text": text
        }
    except Exception as e:
        print(f"Error {url}: {e}")
        return None


with open(INPUT_URLS_FILE, 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Overall: {len(urls)}")


with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(process_url, url): url for url in urls}
    with open(OUTPUT_JSONL, 'w', encoding='utf-8') as outfile:
        outfile.write(f'Date: {time.asctime(local_time)} \n')
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result:
                outfile.write(
                    json.dumps(result, ensure_ascii=False) 
                    + '\n'
                    )
                outfile.flush()
            print(f"Processed {i}/{len(urls)}")
            time.sleep(DELAY) 

print(f"Done! {OUTPUT_JSONL}")