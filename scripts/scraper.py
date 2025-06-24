# ... (import 和 clean_text, get_infobox_data 函数保持不变)
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def clean_text(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_infobox_data(soup):
    # ... (和上一版优化后的函数一样)
    infobox = soup.find('table', {'class': 'infobox'})
    if not infobox: return {}
    data = {}
    rows = infobox.find_all('tr')
    for row in rows:
        header = row.find('th')
        value_cell = row.find('td')
        if header and value_cell:
            key = clean_text(header.text).lower()
            value_text = value_cell.get_text(separator='|', strip=True).split('|')[0]
            val = clean_text(value_text)
            data[key] = val
    return data


def scrape_robot_data(name, url):
    # ... (和上一版优化后的函数一样)
    try:
        response = requests.get(url, headers={'User-Agent': 'Cool-Robot-App-Scraper/1.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        infobox_data = get_infobox_data(soup)
        robot_data = {
            'name': clean_text(soup.find('h1', {'id': 'firstHeading'}).text),
            'manufacturer': infobox_data.get('manufacturer', 'N/A'),
            'type': infobox_data.get('type', 'N/A'),
            'specs': {
                'Weight': infobox_data.get('weight', infobox_data.get('mass', 'N/A')),
                'Payload': infobox_data.get('payload', 'N/A'),
                'Speed': infobox_data.get('speed', 'N/A'),
            },
            'modules': { 'Perception': {'components': ['Cameras', 'IMU', 'Sensors'], 'suppliers': ['Various']}, 'Locomotion': {'components': ['Actuators', 'Legs', 'Motors'], 'suppliers': ['Various']}, }
        }
        print(f"✅ Successfully scraped data for: {name}")
        return robot_data
    except Exception as e:
        print(f"❌ Failed to scrape data for {name}. Error: {e}")
        return None


if __name__ == '__main__':
    WIKI_BASE_URL = 'https://en.wikipedia.org/wiki/'
    all_robots_data = {}

    # 新的核心逻辑：从文件读取目标列表
    try:
        with open('robots_to_scrape.txt', 'r') as f:
            robot_pages = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ `robots_to_scrape.txt` not found. Exiting.")
        robot_pages = []

    print(f"🔥 Found {len(robot_pages)} robots to scrape: {robot_pages}")

    for page_name in robot_pages:
        # 将页面名转换为小写且适合做JSON key的格式
        robot_key = page_name.lower().replace('_(robot)', '').replace('_', ' ')
        robot_url = WIKI_BASE_URL + page_name
        data = scrape_robot_data(robot_key, robot_url)
        if data:
            all_robots_data[robot_key] = data
    
    output = {
        'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        'robots': all_robots_data
    }
    
    with open('data/robots.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print("🚀 Scraping complete. `data/robots.json` has been updated.")
