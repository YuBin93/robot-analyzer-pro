import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

# 从环境变量中获取API Key
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Gemini API Key not found. Please set the GEMINI_API_KEY secret.")

# 配置Google Generative AI SDK
genai.configure(api_key=API_KEY)

# 目标机器人列表保持不变
ROBOT_WIKI_URLS = {
    'spot': 'https://en.wikipedia.org/wiki/Spot_(robot)',
    'atlas': 'https://en.wikipedia.org/wiki/Atlas_(robot)',
    'digit': 'https://en.wikipedia.org/wiki/Digit_(robot)'
}

def build_prompt(page_content):
    """构建一个高质量的Prompt，指导Gemini完成任务"""
    
    desired_json_structure = """
    {
      "name": "Robot's full name",
      "manufacturer": "The company that created the robot",
      "type": "Type of robot (e.g., Quadruped, Humanoid)",
      "specs": {
        "Weight": "Weight of the robot (e.g., 75 kg)",
        "Payload": "Payload capacity (e.g., 25 kg)",
        "Speed": "Maximum speed (e.g., 1.5 m/s)"
      },
      "modules": {
        "Perception": { "components": ["List of sensors like Cameras, LiDAR, IMU"], "suppliers": ["List of potential suppliers"] },
        "Locomotion": { "components": ["List of components like Actuators, Hydraulic systems"], "suppliers": ["List of potential suppliers"] }
      }
    }
    """

    # Gemini 对指令的理解能力很强，我们可以直接要求它输出JSON
    prompt = f"""
    Analyze the following text from a Wikipedia page about a robot.
    Your task is to extract key information and provide the output ONLY in a valid JSON format.
    The JSON object must strictly adhere to the structure shown below.
    If a piece of information is not available in the text, use "N/A" as the value.
    Do not include any introductory text, closing remarks, or markdown formatting like ```json.
    
    ### Desired JSON Structure:
    {desired_json_structure}

    ### Page Content to Analyze:
    ---
    {page_content[:20000]} 
    ---

    ### Extracted JSON Data:
    """
    return prompt

def scrape_with_gemini(name, url):
    """使用Gemini模型抓取单个机器人的数据"""
    print(f"✨ Attempting to scrape '{name}' with Gemini...")
    try:
        # 1. 获取网页纯文本
        response = requests.get(url, headers={'User-Agent': 'Robot-Genesis-Gemini-Scraper/1.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        main_content = soup.find(id='mw-content-text')
        page_text = main_content.get_text(separator=' ', strip=True) if main_content else soup.get_text(separator=' ', strip=True)

        # 2. 构建Prompt
        prompt = build_prompt(page_text)
        
        # 3. 初始化并调用Gemini模型
        model = genai.GenerativeModel('gemini-pro')
        # 添加安全设置，降低因安全策略被阻断的概率
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        # 让模型生成内容
        response = model.generate_content(prompt, safety_settings=safety_settings)
        
        # 4. 解析Gemini返回的结果
        # response.text 直接就是模型生成的字符串
        json_text = response.text
        
        # 验证并加载JSON
        robot_data = json.loads(json_text)
        
        print(f"✅ Successfully parsed Gemini response for: {name}")
        return robot_data

    except Exception as e:
        # 捕获并打印更详细的错误信息
        if 'response' in locals() and hasattr(response, 'prompt_feedback'):
             print(f"Prompt Feedback: {response.prompt_feedback}")
        print(f"❌ Failed to scrape data for '{name}' with Gemini. Error: {e}")
        return None

if __name__ == '__main__':
    all_robots_data = {}
    for name, url in ROBOT_WIKI_URLS.items():
        data = scrape_with_gemini(name, url)
        if data:
            all_robots_data[name] = data
            
    output = {
        'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        'robots': all_robots_data
    }
    
    with open('data/robots.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print("🚀 Gemini-driven scraping complete. `data/robots.json` has been updated.")
