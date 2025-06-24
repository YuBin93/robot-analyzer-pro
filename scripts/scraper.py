import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# 我们要抓取数据的机器人及其维基百科页面URL
# 以后想添加新机器人，只需要在这里加上新条目即可
ROBOT_WIKI_URLS = {
    'spot': 'https://en.wikipedia.org/wiki/Spot_(robot)',
    # 'atlas': 'https://en.wikipedia.org/wiki/Atlas_(robot)', # 可以取消注释来添加Atlas
}

def get_infobox_data(soup):
    """从维基百科的infobox中提取关键信息"""
    infobox = soup.find('table', {'class': 'infobox'})
    if not infobox:
        return {}

    data = {}
    rows = infobox.find_all('tr')
    for row in rows:
        header = row.find('th')
        value = row.find('td')
        if header and value:
            # 清理文本
            key = header.text.strip().lower()
            val = value.text.strip()
            data[key] = val
    return data

def scrape_robot_data(name, url):
    """抓取单个机器人的数据并格式化"""
    try:
        response = requests.get(url, headers={'User-Agent': 'Cool-Robot-App-Scraper/1.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        infobox_data = get_infobox_data(soup)
        
        # 将抓取到的数据映射到我们的数据结构中
        # 这是最需要定制的部分，因为每个页面的字段名都不同
        robot_data = {
            'name': soup.find('h1', {'id': 'firstHeading'}).text.strip(),
            'manufacturer': infobox_data.get('manufacturer', 'N/A'),
            'type': infobox_data.get('type', 'Robot'),
            'specs': {
                'Weight': infobox_data.get('weight', 'N/A'),
                'Payload': infobox_data.get('payload', 'N/A'),
                'Speed': infobox_data.get('speed', 'N/A'),
            },
            # 模块和供应商信息通常很难从维基百科抓取，这里用占位符
            'modules': {
                'Perception': {'components': ['Cameras', 'IMU'], 'suppliers': ['Various']},
                'Locomotion': {'components': ['Actuators', 'Legs'], 'suppliers': ['Various']},
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
