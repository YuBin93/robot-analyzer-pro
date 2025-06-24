import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

# 我们要抓取数据的机器人及其维基百科页面URL
ROBOT_WIKI_URLS = {
    'spot': 'https://en.wikipedia.org/wiki/Spot_(robot)',
    # 以后可以继续在这里添加，比如 'atlas': '...'
}

def clean_text(text):
    """一个更强大的文本清理函数，去除引用标记如[1]和多余的换行"""
    # 去除引用标记，例如 [1], [2], [a], etc.
    text = re.sub(r'\[.*?\]', '', text)
    # 将换行符和多个空格替换为单个空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_infobox_data(soup):
    """从维基百科的infobox中提取关键信息（优化版）"""
    infobox = soup.find('table', {'class': 'infobox'})
    if not infobox:
        return {}

    data = {}
    rows = infobox.find_all('tr')
    for row in rows:
        header = row.find('th')
        value_cell = row.find('td')
        
        if header and value_cell:
            # 将key转换为小写，便于统一处理
            key = clean_text(header.text).lower()
            # 获取value，并只取第一个<br>之前的内容（处理多行数据）
            value_text = value_cell.get_text(separator='|', strip=True).split('|')[0]
            val = clean_text(value_text)
            data[key] = val
            
    return data

def scrape_robot_data(name, url):
    """抓取单个机器人的数据并格式化（优化版）"""
    try:
        response = requests.get(url, headers={'User-Agent': 'Cool-Robot-App-Scraper/1.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        infobox_data = get_infobox_data(soup)
        
        # 将抓取到的数据映射到我们的数据结构中
        # 这里我们用 .get() 方法，并检查多个可能的key，提高鲁棒性
        robot_data = {
            'name': clean_text(soup.find('h1', {'id': 'firstHeading'}).text),
            'manufacturer': infobox_data.get('manufacturer', 'N/A'),
            'type': infobox_data.get('type', 'N/A'),
            'specs': {
                'Weight': infobox_data.get('weight', infobox_data.get('mass', 'N/A')),
                'Payload': infobox_data.get('payload', 'N/A'),
                'Speed': infobox_data.get('speed', 'N/A'),
            },
            # 模块和供应商信息仍然使用占位符，因为这部分信息很难从通用页面抓取
            'modules': {
                'Perception': {'components': ['Cameras', 'IMU', 'Sensors'], 'suppliers': ['Various']},
                'Locomotion': {'components': ['Actuators', 'Legs', 'Motors'], 'suppliers': ['Various']},
            }
        }
        print(f"✅ Successfully scraped data for: {name}")
        return robot_data
    except Exception as e:
        print(f"❌ Failed to scrape data for {name}. Error: {e}")
        return None

if __name__ == '__main__':
    all_robots_data = {}
    for name, url in ROBOT_WIKI_URLS.items():
        data = scrape_robot_data(name, url)
        if data:
            all_robots_data[name] = data
            
    # 准备最终的JSON输出
    output = {
        'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        'robots': all_robots_data
    }
    
    # 将结果写入我们的数据文件
    with open('data/robots.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print("🚀 Scraping complete. `data/robots.json` has been updated.")
