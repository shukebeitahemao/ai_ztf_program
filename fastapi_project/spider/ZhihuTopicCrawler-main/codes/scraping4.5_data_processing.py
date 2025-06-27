"""
知乎爬虫 - 数据整理脚本：合并所有回答数据并提取用户列表
================================================

🎯 功能说明：
- 将所有问题的回答数据合并成一个大文件
- 提取所有回答者的用户token，为下一步爬取作者信息做准备
- 数据去重和整理

📊 数据流程：
1. 读取 data/answers_of_question/ 目录下的所有CSV文件
2. 合并所有回答数据到 all_answers.csv
3. 提取唯一的用户token到 user_tokens.csv
4. 统计和输出处理结果

💡 使用场景：
- 在 scraping3 完成后运行
- 为 scraping5（爬取作者信息）做准备
- 便于后续数据分析

上次运行：2024/11/16 15:05
"""

import os
import pandas as pd

# 数据文件配置
folder_path = "data/answers_of_question"  # 存放各个问题回答数据的文件夹
print(f"📂 正在处理文件夹: {folder_path}")

# 获取所有CSV文件的路径列表
filename_list = [
    os.path.join(folder_path, file) 
    for file in os.listdir(folder_path) 
    if file.endswith(".csv")
]
print(f"📄 找到 {len(filename_list)} 个CSV文件")

# 创建生成器对象，逐个读取CSV文件（节省内存）
dfs = (pd.read_csv(file) for file in filename_list)

# 合并所有DataFrame
print("🔄 正在合并所有回答数据...")
merged_df = pd.concat(dfs, axis=0, ignore_index=True)

# 提取唯一的用户token和用户名
print("👥 正在提取用户信息...")
user_token_df = merged_df.loc[:, ["au_urltoken", "au_name"]].drop_duplicates(subset=["au_urltoken"])

# 保存合并后的所有回答数据
print("💾 正在保存数据...")
merged_df.to_csv("data/all_answers.csv", index=False, encoding="utf-8")

# 保存用户token列表（不包含表头，方便scraping5使用）
user_token_df.to_csv("data/user_tokens.csv", index=False, encoding="utf-8", header=False)

# 输出统计信息
print("✅ 数据处理完成！")
print(f"📊 统计结果：")
print(f"   - 处理了 {len(filename_list)} 个问题")
print(f"   - 合并了 {len(merged_df)} 条回答")
print(f"   - 提取了 {len(user_token_df)} 个不重复用户")
print(f"📁 输出文件：")
print(f"   - data/all_answers.csv: 所有回答数据")
print(f"   - data/user_tokens.csv: 用户token列表")
