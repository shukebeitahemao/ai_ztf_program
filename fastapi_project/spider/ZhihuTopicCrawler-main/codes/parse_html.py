#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知乎HTML页面解析脚本
功能：使用get_url_text获取网页HTML内容，解析热门问题信息，提取title、id、url、abstract、hot等信息并保存到CSV文件
作者：AI助手
创建时间：2025-01-20
修改时间：2025-01-20
"""

import os
import re
import csv
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from get_url_text import get_url_text

def parse_html_from_url(url):
    """
    从URL获取HTML内容并提取热门问题信息
    
    Args:
        url (str): 要解析的网页URL
        
    Returns:
        list: 包含解析结果的字典列表
    """
    print(f"🌐 开始获取网页内容: {url}")
    
    # 使用get_url_text获取网页内容
    try:
        html_content = get_url_text(url)
        if not html_content:
            print("❌ 获取网页内容失败：返回内容为空")
            return []
        print(f"✅ 成功获取网页内容，长度: {len(html_content)} 字符")
    except Exception as e:
        print(f"❌ 获取网页内容失败: {e}")
        return []
    
    # 使用BeautifulSoup解析HTML
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        print("✅ HTML解析成功")
    except Exception as e:
        print(f"❌ HTML解析失败: {e}")
        return []
    
    # 查找所有的section元素
    sections = soup.find_all('section', class_='HotItem')
    print(f"📊 找到 {len(sections)} 个热门问题section")
    
    if len(sections) == 0:
        print("⚠️ 未找到任何热门问题section，可能网页结构已变化")
        # 尝试查找其他可能的结构
        print("🔍 尝试查找其他可能的问题容器...")
        alternative_sections = soup.find_all(['div', 'article'], class_=lambda x: x and ('item' in x.lower() or 'question' in x.lower()))
        if alternative_sections:
            print(f"📊 找到 {len(alternative_sections)} 个可能的问题容器")
            sections = alternative_sections
        else:
            print("❌ 未找到任何问题相关的容器")
    
    results = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for i, section in enumerate(sections, 1):
        try:
            print(f"\n🔍 正在解析第 {i} 个section...")
            
            # 提取title - 尝试多种可能的选择器
            title_element = section.find('h2', class_='HotItem-title')
            if not title_element:
                # 尝试其他可能的标题选择器
                title_element = section.find(['h1', 'h2', 'h3'], class_=lambda x: x and ('title' in x.lower()))
                if not title_element:
                    title_element = section.find(['h1', 'h2', 'h3'])
            
            title = title_element.get_text(strip=True) if title_element else ""
            print(f"📝 标题: {title[:50]}...")
            
            # 提取URL和ID - 从a标签的href属性中获取
            link_element = section.find('a', href=True)
            if not link_element:
                # 尝试查找任何包含href的链接
                link_element = section.find('a')
            
            url_link = ""
            question_id = ""
            
            if link_element and link_element.get('href'):
                url_link = link_element['href']
                # 如果是相对路径，补充完整URL
                if url_link.startswith('/'):
                    url_link = f"https://www.zhihu.com{url_link}"
                
                # 使用正则表达式提取问题ID
                match = re.search(r'/question/(\d+)', str(url_link))
                if match:
                    question_id = match.group(1)
                print(f"🔗 URL: {url_link}")
                print(f"🆔 ID: {question_id}")
            
            # 提取abstract - 尝试多种可能的选择器
            excerpt_element = section.find('p', class_='HotItem-excerpt')
            if not excerpt_element:
                # 尝试其他可能的摘要选择器
                excerpt_element = section.find('p', class_=lambda x: x and ('excerpt' in x.lower() or 'summary' in x.lower()))
                if not excerpt_element:
                    excerpt_element = section.find('p')
            
            abstract = excerpt_element.get_text(strip=True) if excerpt_element else ""
            # 清理abstract文本，去除多余的空白字符
            abstract = re.sub(r'\s+', ' ', abstract)
            print(f"📄 摘要: {abstract[:50]}...")
            
            # 提取热度信息 - 从包含"热度"的文本中提取
            hot = ""
            # 查找包含热度信息的文本
            hot_text = section.get_text()
            hot_match = re.search(r'(\d+(?:\.\d+)?)\s*万?\s*热度', hot_text)
            if hot_match:
                hot_value = hot_match.group(1)
                if '万' in hot_match.group(0):
                    hot = f"{hot_value}万热度"
                else:
                    hot = f"{hot_value}热度"
            else:
                # 尝试其他热度格式
                hot_match2 = re.search(r'(\d+(?:\.\d+)?)\s*万?\s*(关注|浏览|阅读)', hot_text)
                if hot_match2:
                    hot_value = hot_match2.group(1)
                    hot_type = hot_match2.group(2)
                    if '万' in hot_match2.group(0):
                        hot = f"{hot_value}万{hot_type}"
                    else:
                        hot = f"{hot_value}{hot_type}"
            
            print(f"🔥 热度: {hot}")
            
            # 只有当获取到基本信息时才添加到结果中
            if title or question_id:
                # 构建结果字典
                result = {
                    'type': '热点问题',
                    'id': question_id,
                    'title': title,
                    'url': url_link,
                    'date': current_date,
                    'hot': hot,
                    'abstract': abstract
                }
                
                results.append(result)
                print(f"✅ 第 {i} 个section解析完成")
            else:
                print(f"⚠️ 第 {i} 个section缺少关键信息，跳过")
            
        except Exception as e:
            print(f"❌ 解析第 {i} 个section时出错: {e}")
            continue
    
    print(f"\n📊 总共成功解析 {len(results)} 条记录")
    return results

def parse_html_file(html_file_path):
    """
    解析本地HTML文件（保留原功能作为备用）
    
    Args:
        html_file_path (str): HTML文件路径
        
    Returns:
        list: 包含解析结果的字典列表
    """
    print(f"📖 开始解析本地HTML文件: {html_file_path}")
    
    # 读取HTML文件内容
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        print(f"✅ 成功读取HTML文件")
    except Exception as e:
        print(f"❌ 读取HTML文件失败: {e}")
        return []
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查找所有的section元素
    sections = soup.find_all('section', class_='HotItem')
    print(f"📊 找到 {len(sections)} 个热门问题section")
    
    results = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for i, section in enumerate(sections, 1):
        try:
            print(f"\n🔍 正在解析第 {i} 个section...")
            
            # 提取title - 从h2标签中获取
            title_element = section.find('h2', class_='HotItem-title')
            title = title_element.get_text(strip=True) if title_element else ""
            print(f"📝 标题: {title[:50]}...")
            
            # 提取URL和ID - 从a标签的href属性中获取
            link_element = section.find('a', href=True)
            url = ""
            question_id = ""
            
            if link_element and link_element.get('href'):
                url = link_element['href']
                # 使用正则表达式提取问题ID
                match = re.search(r'/question/(\d+)', url)
                if match:
                    question_id = match.group(1)
                print(f"🔗 URL: {url}")
                print(f"🆔 ID: {question_id}")
            
            # 提取abstract - 从p标签中获取
            excerpt_element = section.find('p', class_='HotItem-excerpt')
            abstract = excerpt_element.get_text(strip=True) if excerpt_element else ""
            # 清理abstract文本，去除多余的空白字符
            abstract = re.sub(r'\s+', ' ', abstract)
            print(f"📄 摘要: {abstract[:50]}...")
            
            # 提取热度信息 - 从包含"热度"的文本中提取
            hot = ""
            # 查找包含热度信息的文本
            hot_text = section.get_text()
            hot_match = re.search(r'(\d+(?:\.\d+)?)\s*万?\s*热度', hot_text)
            if hot_match:
                hot_value = hot_match.group(1)
                if '万' in hot_match.group(0):
                    hot = f"{hot_value}万热度"
                else:
                    hot = f"{hot_value}热度"
            print(f"🔥 热度: {hot}")
            
            # 构建结果字典
            result = {
                'type': '热点问题',
                'id': question_id,
                'title': title,
                'url': url,
                'date': current_date,
                'hot': hot,
                'abstract': abstract
            }
            
            results.append(result)
            print(f"✅ 第 {i} 个section解析完成")
            
        except Exception as e:
            print(f"❌ 解析第 {i} 个section时出错: {e}")
            continue
    
    print(f"\n📊 总共成功解析 {len(results)} 条记录")
    return results

def save_to_csv(data, output_file):
    """
    将数据保存到CSV文件
    
    Args:
        data (list): 要保存的数据列表
        output_file (str): 输出文件路径
    """
    if not data:
        print("❌ 没有数据可保存")
        return
    
    print(f"💾 开始保存数据到: {output_file}")
    
    # 确保目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 创建目录: {output_dir}")
    
    try:
        # 使用pandas保存数据
        df = pd.DataFrame(data)
        
        # 重新排列列的顺序
        columns_order = ['type', 'id', 'title', 'url', 'date', 'hot', 'abstract']
        #先取得前5列，验证不是列名问题
        df = df[columns_order].iloc[:,:5]
        
        # 保存到CSV文件
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ 成功保存 {len(data)} 条记录到: {output_file}")
        
        # 验证文件是否保存成功
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"📊 文件大小: {file_size} bytes")
            
            # 读取并显示前几行作为验证
            try:
                verify_df = pd.read_csv(output_file, nrows=3)
                print(f"📋 文件内容预览:")
                print(verify_df[['type', 'id', 'title', 'hot']].to_string())
            except Exception as e:
                print(f"⚠️ 验证文件内容时出错: {e}")
        else:
            print("❌ 文件保存后未找到！")
            
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    主函数：执行HTML解析和数据保存流程
    """
    print("🚀 开始执行知乎热门问题网页解析脚本")
    print("=" * 60)
    
    # 获取用户输入的URL（可以在这里修改为具体的URL）
    #target_url = input("🔗 请输入要解析的知乎页面URL（或直接按Enter使用默认测试URL）: ").strip()
    target_url = "https://www.zhihu.com/hot"
    # 如果用户没有输入URL，可以使用默认的测试URL或检查本地文件
    if not target_url:
        print("⚠️ 未输入URL，尝试使用本地text.html文件...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        html_file = os.path.join(script_dir, "text.html")
        
        if os.path.exists(html_file):
            print(f"📁 使用本地HTML文件: {html_file}")
            results = parse_html_file(html_file)
        else:
            print("❌ 本地HTML文件不存在，请提供URL")
            return
    else:
        print(f"🌐 目标URL: {target_url}")
        # 从URL获取并解析HTML内容
        results = parse_html_from_url(target_url)
    
    if results:
        # 设置输出文件路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_dir, "..", "data", "question_list.csv")
        
        # 保存结果到CSV文件

        save_to_csv(results, output_file)
        print("\n🎉 脚本执行完成！")
        print(f"📋 解析结果已保存到: {output_file}")
    else:
        print("\n❌ 没有解析到任何数据")

if __name__ == "__main__":
    main() 