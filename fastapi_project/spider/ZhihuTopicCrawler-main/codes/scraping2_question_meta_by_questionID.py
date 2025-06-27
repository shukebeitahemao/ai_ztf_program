"""
知乎爬虫 - 第二步：根据问题ID获取问题详细元数据（修复版）
==============================================

🎯 功能说明：
- 输入：问题ID列表
- 输出：问题的详细元数据（问题标题、回答数、关注数、浏览数、标签等）
- 用途：获取每个问题的详细统计信息，为后续分析提供基础数据

📊 数据流程：
1. 读取 question_list.csv（由scraping1生成）
2. 对每个问题访问其详情页面
3. 解析HTML页面获取元数据
4. 保存到 question_meta_info.csv

⚠️ 注意事项：
- 需要先运行 scraping1 获取问题列表
- 每次最好限制在250条以内，避免触发反爬机制
- 建议设置时间过滤条件，只爬取最近的问题
- 已修复403错误和空文件读取问题

修复版本：2025/06/20
上次运行：2024/11/16 12:51
"""

import os
import time
import random
import pandas as pd
from bs4 import BeautifulSoup as bs  # HTML解析库，用于从网页中提取数据
from get_url_text import get_url_text  # 自定义的网络请求模块

def get_question_list(filename):
    """
    📖 读取问题列表并进行筛选
    
    参数：
        filename: 问题列表CSV文件路径（通常是question_list.csv）
    
    返回：
        q_list: 筛选后的问题列表
    
    筛选条件：
        1. 排除专栏文章（type != "专栏"）
        2. 只保留指定日期后的问题（可根据需要调整）
    """
    try:
        df = pd.read_csv(filename)
        print(f"✅ 成功读取问题列表文件: {filename}")
        print(f"📊 原始数据包含 {len(df)} 条记录")
        
        # 显示文件的列名
        print(f"📋 数据列名: {list(df.columns)}")
        
        # 筛选条件1：排除专栏文章，只保留问题和回答
        if "type" in df.columns:
            original_count = len(df)
            df = df[df["type"] != "专栏"]
            print(f"🔍 排除专栏文章后剩余: {len(df)} 条记录 (删除了 {original_count - len(df)} 条)")
        
        # 筛选条件2：只爬取指定日期之后的问题（可根据需要修改）
        if "date" in df.columns:
            original_count = len(df)
            df = df[df["date"] >= "2025-06-15"]  # 调整为更近的日期
            print(f"🗓️  筛选2025-06-15后的问题: {len(df)} 条记录 (删除了 {original_count - len(df)} 条)")
        
        # 限制数量，避免触发反爬虫
        if len(df) > 10:  # 限制为10条，更安全
            df = df.head(10)
            print(f"⚠️  为避免反爬虫，限制处理前10条记录")
        
        # 转换为列表格式，方便后续处理
        q_list = df.values.tolist()
        print(f"📝 最终将处理 {len(q_list)} 条问题")
        return q_list
        
    except FileNotFoundError:
        print(f"❌ 错误：找不到文件 {filename}")
        print("💡 请先运行 scraping1_questions_by_topicID.py 生成问题列表")
        return []
    except Exception as e:
        print(f"❌ 读取问题列表时出错: {e}")
        return []

def get_question_data(html_text, q_id):
    """
    🔍 从HTML页面中解析问题的元数据
    
    参数：
        html_text: 问题详情页的HTML源码
        q_id: 问题ID（用于错误处理）
    
    返回：
        list: 包含问题各项元数据的列表
              [问题ID, 问题标题, 关注数, 浏览数, 回答数, 话题标签, 创建日期]
    
    解析的元数据包括：
        - qContent: 问题标题
        - followerCount: 关注该问题的人数
        - viewCount: 问题浏览量
        - answerCount: 回答数量
        - topicTag: 问题所属的话题标签
        - date: 问题创建日期
    """

    try:
        bsobj = bs(html_text, "html.parser")
        
        # 检查是否成功获取到HTML内容
        if not html_text or len(html_text) < 100:
            print(f"⚠️  问题 {q_id} 的HTML内容异常，长度: {len(html_text) if html_text else 0}")
            return [q_id, "EmptyHTML", "0", "0", "0", "未知", "2025-01-01"]

        # 尝试提取问题标题
        try:
            qContent_elements = bsobj.find_all("meta", attrs={"itemprop": "name"})
            if qContent_elements:
                qContent = qContent_elements[0].get("content", "未知标题")
            else:
                # 备用方案：尝试从title标签获取
                title_element = bsobj.find("title")
                qContent = title_element.get_text() if title_element else "未知标题"
        except Exception as e:
            print(f"⚠️  提取标题失败: {e}")
            qContent = "标题提取失败"

        # 尝试提取关注数和浏览数
        try:
            number_boards = bsobj.find_all("strong", attrs={"class": "NumberBoard-itemValue"})
            if len(number_boards) >= 2:
                followerCount = number_boards[0].get("title", "0")
                viewCount = number_boards[1].get("title", "0")
            else:
                followerCount = "0"
                viewCount = "0"
        except Exception as e:
            print(f"⚠️  提取关注数/浏览数失败: {e}")
            followerCount = "0"
            viewCount = "0"

        # 尝试提取回答数
        try:
            answerCount_elements = bsobj.find_all("meta", attrs={"itemprop": "answerCount"})
            if answerCount_elements:
                answerCount = answerCount_elements[0].get("content", "0")
            else:
                answerCount = "0"
        except Exception as e:
            print(f"⚠️  提取回答数失败: {e}")
            answerCount = "0"

        # 尝试提取话题标签
        try:
            topicTag_elements = bsobj.find_all("meta", attrs={"itemprop": "keywords"})
            if topicTag_elements:
                topicTag = topicTag_elements[0].get("content", "未知话题")
            else:
                topicTag = "未知话题"
        except Exception as e:
            print(f"⚠️  提取话题标签失败: {e}")
            topicTag = "未知话题"

        # 尝试提取创建日期
        try:
            date_elements = bsobj.find_all("meta", attrs={"itemprop": "dateCreated"})
            if date_elements:
                date = date_elements[0].get("content", "2025-01-01")
                date = date[:10]  # 只取日期部分
            else:
                date = "2025-01-01"
        except Exception as e:
            print(f"⚠️  提取创建日期失败: {e}")
            date = "2025-01-01"

        print(f"✅ 成功解析问题 {q_id}: {qContent[:30]}...")
        return [q_id, qContent, followerCount, viewCount, answerCount, topicTag, date]

    except Exception as e:
        print(f"❌ 解析问题 {q_id} 时发生严重错误: {e}")
        return [q_id, "ParseError", "0", "0", "0", "解析错误", "2025-01-01"]

def save_data(q_info_list, filename):
    """
    💾 保存问题元数据到CSV文件（修复版）
    
    参数：
        q_info_list: 问题信息列表
        filename: 输出文件名（通常是question_meta_info.csv）
    
    数据处理逻辑：
        1. 创建DataFrame并设置列名
        2. 如果文件已存在且不为空，则合并新旧数据
        3. 清理无效数据（UnknownError）
        4. 按问题ID去重，保留最新数据
        5. 格式化日期并排序
        6. 保存到CSV文件
    """
    if not q_info_list:
        print("⚠️  没有数据需要保存")
        return
        
    # 创建DataFrame，设置列名
    df = pd.DataFrame(
        q_info_list,
        columns=[
            "q_id",           # 问题ID
            "q_content",      # 问题标题
            "followerCount",  # 关注数
            "viewCount",      # 浏览数
            "answerCount",    # 回答数
            "topicTag",       # 话题标签
            "created_date"    # 创建日期
        ],
    )
    
    print(f"📊 准备保存 {len(df)} 条记录到 {filename}")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # 如果文件已经存在且不为空，合并新旧数据
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            df_old = pd.read_csv(filename)
            print(f"📖 读取到旧数据 {len(df_old)} 条记录")
            df = pd.concat([df_old, df], ignore_index=True)
            
            # 数据清理：删除解析失败的问题（标记为UnknownError、EmptyHTML等的记录）
            error_conditions = df["q_content"].isin(["UnknownError", "EmptyHTML", "ParseError", "标题提取失败"])
            error_count = error_conditions.sum()
            if error_count > 0:
                print(f"🧹 清理 {error_count} 条错误记录")
                df = df[~error_conditions]
            
            # 按问题ID去重，保留最新的数据
            original_count = len(df)
            df = df.drop_duplicates(subset=["q_id"], keep="last")
            duplicate_count = original_count - len(df)
            if duplicate_count > 0:
                print(f"🔄 去重 {duplicate_count} 条重复记录")
            
        except Exception as e:
            print(f"⚠️  读取旧文件失败，将创建新文件: {e}")
    
    try:
        # 日期格式化：确保日期格式一致
        df["created_date"] = pd.to_datetime(df["created_date"], errors='coerce')
        df["created_date"] = df["created_date"].dt.strftime('%Y-%m-%d')
        
        # 按创建日期排序
        df = df.sort_values(by=["created_date"], ascending=False)  # 最新的在前
        
        # 保存到CSV文件，使用UTF-8编码以支持中文
        df.to_csv(filename, index=False, header=True, encoding="utf-8")
        print(f"✅ 成功保存 {len(df)} 条记录到 {filename}")
        
        # 显示保存的数据预览
        if len(df) > 0:
            print("📋 数据预览（最新3条）:")
            preview_df = df.head(3)[['q_id', 'q_content', 'answerCount', 'followerCount']]
            for idx, row in preview_df.iterrows():
                print(f"  - {row['q_id']}: {row['q_content'][:40]}... (回答:{row['answerCount']}, 关注:{row['followerCount']})")
        
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    主函数：执行问题元数据爬取流程
    """
    print("🚀 开始执行知乎问题元数据爬取脚本")
    print("=" * 60)
    
    # 读取问题列表
    q_list = get_question_list("data/question_list.csv")
    if not q_list:
        print("❌ 无法获取问题列表，程序退出")
        return
    
    print(f"📊 共 {len(q_list)} 个问题待处理")
    q_info_list = []
    success_count = 0
    error_count = 0

    # 处理每个问题
    for i, item in enumerate(q_list):
        try:
            # 获取问题ID（根据实际CSV结构调整索引）
            if len(item) > 1:
                q_id = item[1]  # 假设ID在第二列
            else:
                q_id = item[0]  # 如果只有一列
            
            print(f"\n🔍 处理问题 {i+1}/{len(q_list)}: ID={q_id}")
            
            # 构建问题URL
            url = f"https://www.zhihu.com/question/{str(q_id)}"
            
            # 获取网页内容
            text = get_url_text(url)
            
            if not text:
                print(f"❌ 无法获取问题 {q_id} 的网页内容")
                error_count += 1
                # 添加错误记录
                q_info_list.append([q_id, "NetworkError", "0", "0", "0", "网络错误", "2025-01-01"])
                continue
            
            # 解析问题数据
            q_info = get_question_data(text, q_id)
            q_info_list.append(q_info)
            
            if q_info[1] not in ["NetworkError", "EmptyHTML", "ParseError", "标题提取失败"]:
                success_count += 1
            else:
                error_count += 1

            # 每处理30个问题保存一次，避免数据丢失
            if (i + 1) % 30 == 0 or (i + 1) == len(q_list):
                print(f"\n💾 保存进度：已处理 {i+1} 个问题")
                save_data(q_info_list, "data/question_meta_info.csv")
                q_info_list = []  # 清空列表，准备下一批
                
                # 添加随机延迟，避免触发反爬虫
                delay = random.uniform(2, 5)
                print(f"⏰ 休息 {delay:.1f} 秒...")
                time.sleep(delay)

        except Exception as e:
            print(f"❌ 处理问题时出错: {e}")
            error_count += 1
            continue

    # 最终保存
    if q_info_list:
        save_data(q_info_list, "data/question_meta_info.csv")

    print(f"\n🎉 脚本执行完成！")
    print(f"📊 统计信息:")
    print(f"  - 总处理数: {len(q_list)}")
    print(f"  - 成功数: {success_count}")
    print(f"  - 失败数: {error_count}")
    print(f"  - 成功率: {success_count/(len(q_list)) * 100:.1f}%")

# 代码一次只能跑250条，之后会变乱码，需要手动去浏览器更新cookie
# 2024/11/16更新：似乎不会再变乱码了，建议保持关注
# 2025/06/20更新：修复了403错误和空文件读取问题
if __name__ == "__main__":
    main()
