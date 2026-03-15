import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# --- Настройки ---
MAIN_URL = "https://pja.edu.pl"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

BASE_DOMAIN = "pja.edu.pl"

def is_valid_url(url):
    if not url:
        return False
    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc != BASE_DOMAIN:
        return False
    # Исключаем якоря (если нужны только уникальные страницы)
    if parsed.fragment:
        return False

    exclude_extensions = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.zip')
    if parsed.path.lower().endswith(exclude_extensions):
        return False
    return True


print(f"Download {MAIN_URL} ...")
try:
    response = requests.get(MAIN_URL, headers=HEADERS, timeout=10)
    response.encoding = 'utf-8' 
    response.raise_for_status()
except Exception as e:
    print(f"Error: {e}")
    exit()


soup = BeautifulSoup(response.text, 'html.parser')

link_elements = soup.select("li a")

found_urls = set()
for a in link_elements:
    href = a.get("href")
    if not href:
        continue
    absolute_url = urljoin(MAIN_URL, href)
    if is_valid_url(absolute_url):
        found_urls.add(absolute_url)

print(f"Найдено {len(found_urls)} уникальных внутренних ссылок в <li>:")
for url in sorted(found_urls):
    print(url)


all_links = soup.find_all("a", href=True)
all_urls = set()

for a in all_links:
    href = a["href"]
    absolute_url = urljoin(MAIN_URL, href)
    if is_valid_url(absolute_url):
        all_urls.add(absolute_url)

with open("urls.txt", "w", encoding="utf-8") as f:
    for a in all_urls:
        f.write(a+"\n")


print(f"Overall: {len(all_urls)}")
