"""
知乎爬虫 - 简单测试脚本
==================

🎯 功能说明：
- 检查 question_list.csv 文件是否存在
- 用于验证第一步爬虫是否成功运行

💡 使用方法：
- 运行此脚本，如果输出1，说明文件存在
- 如果没有输出，说明需要先运行 scraping1
"""

import os

# 检查问题列表文件是否存在
if os.path.exists("..\\data\\question_list.csv"):
    print("✅ question_list.csv 文件存在，第一步爬虫运行成功！")
else:
    print("❌ question_list.csv 文件不存在，请先运行 scraping1_questions_by_topicID.py")