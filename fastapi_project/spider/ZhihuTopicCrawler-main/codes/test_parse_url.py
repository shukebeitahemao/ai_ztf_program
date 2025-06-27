#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试URL解析功能的脚本
"""

import os
import sys
from parse_html import parse_html_from_url, save_to_csv

def test_url_parsing():
    """
    测试URL解析功能
    """
    print("🧪 开始测试URL解析功能")
    print("=" * 50)
    
    # 测试URL（这里可以替换为实际的知乎热榜URL）
    test_url = "https://www.zhihu.com/hot"
    
    print(f"🌐 测试URL: {test_url}")
    
    # 调用解析函数
    try:
        results = parse_html_from_url(test_url)
        
        if results:
            print(f"✅ 解析成功，获得 {len(results)} 条记录")
            
            # 显示前几条记录
            for i, result in enumerate(results[:3], 1):
                print(f"\n📋 记录 {i}:")
                print(f"  标题: {result['title'][:50]}...")
                print(f"  ID: {result['id']}")
                print(f"  热度: {result['hot']}")
                print(f"  URL: {result['url']}")
            
            # 保存到测试文件
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_file = os.path.join(script_dir, "..", "data", "test_hot_questions.csv")
            save_to_csv(results, output_file)
            
        else:
            print("❌ 解析失败，未获得任何记录")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_url_parsing() 