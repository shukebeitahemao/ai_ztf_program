
import requests
from bs4 import BeautifulSoup
import time


def crawl_baidu():
    """
    爬取百度首页的函数
    返回: 百度首页的HTML内容
    """
    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 发送GET请求获取百度首页
        response = requests.get('https://www.baidu.com', headers=headers)
        
        # 确保请求成功
        response.raise_for_status()
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 返回解析后的HTML内容
        return soup.prettify()
        
    except requests.RequestException as e:
        print(f"爬取过程中发生错误: {e}")
        return None

# 测试函数
if __name__ == "__main__":
    result = crawl_baidu()
    if result:
        print("成功爬取百度首页！")
        print(result[:500])  # 只打印前500个字符
