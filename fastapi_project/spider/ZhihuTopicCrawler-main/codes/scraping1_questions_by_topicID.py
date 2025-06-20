"""
知乎爬虫 - 第一步：根据话题ID获取问题列表
=====================================

🎯 功能说明：
- 输入：知乎话题ID列表
- 输出：该话题下的所有问题列表（包含问题ID、标题、URL、日期等）
- 用途：这是整个爬虫流程的第一步，为后续步骤提供问题数据源

📊 数据来源：
- 讨论区：essence + timeline_activity
- 精华区：top_activity  
- 等待回答：top_question + new_question

🚀 核心API：
- https://www.zhihu.com/api/v5.1/topics/{话题ID}/feeds/{类型}
- 支持分页获取，自动处理所有页面

⚠️ 注意事项：
- 需要有效的cookie才能访问API
- 可能会触发403错误，需要更新认证信息
- 支持多个话题ID同时爬取

上次运行：2024/11/16 12:32
"""


import os
import json
import pandas as pd
from datetime import datetime
from get_url_text import get_url_text



def parseJson(text, q_list):
    """
    🔍 解析知乎API返回的JSON数据，提取问题、回答、文章信息
    
    参数:
        text: 从知乎API获取的JSON字符串
        q_list: 问题列表，用于存储解析结果
    
    返回:
        nextUrl: 下一页的URL链接，用于分页爬取
    """
    # 将JSON字符串转换为Python字典对象
    json_data = json.loads(text)
    
    # 提取数据列表，包含当前页面的所有内容项
    lst = json_data["data"]
    
    # 提取分页信息中的下一页URL，用于继续爬取后续页面
    nextUrl = json_data["paging"]["next"]

    # 如果当前页面没有数据，直接返回（防止空页面继续处理）
    if not lst:
        return

    # 遍历当前页面的每一个内容项（问题、回答或文章）
    for item in lst:
        # 获取内容类型：answer(回答)、question(问题)、article(文章)
        type = item["target"]["type"]

        if type == "answer":
            # 🎯 处理"回答"类型的数据
            # 这种情况是通过回答发现的问题，标记为特殊类型
            cn_type = "问题_来自回答"
            
            # 从回答数据中提取对应的问题信息
            question = item["target"]["question"]
            
            # 提取问题的唯一标识符
            id = question["id"]
            
            # 提取问题的标题文本
            title = question["title"]
            
            # 构造问题的完整URL链接
            url = "https://www.zhihu.com/question/" + str(id)
            
            # 将Unix时间戳转换为可读的日期格式(YYYY-MM-DD)
            question_date = datetime.fromtimestamp(question["created"]).strftime(
                "%Y-%m-%d"
            )
            
            # 构造数据列表：[类型, ID, 标题, URL, 日期]
            sml_list = [cn_type, id, title, url, question_date]
            
            # 将数据添加到全局问题列表中
            q_list.append(sml_list)

        elif type == "question":
            # 🎯 处理"问题"类型的数据
            # 这是直接从话题页面获取的问题
            cn_type = "问题"
            
            # 问题数据就在target层级中，不需要再下一层
            question = item["target"]
            
            # 提取问题的唯一标识符
            id = question["id"]
            
            # 提取问题的标题文本
            title = question["title"]
            
            # 构造问题的完整URL链接
            url = "https://www.zhihu.com/question/" + str(id)
            
            # 将Unix时间戳转换为可读的日期格式(YYYY-MM-DD)
            question_date = datetime.fromtimestamp(question["created"]).strftime(
                "%Y-%m-%d"
            )
            
            # 构造数据列表：[类型, ID, 标题, URL, 日期]
            sml_list = [cn_type, id, title, url, question_date]
            
            # 将数据添加到全局问题列表中
            q_list.append(sml_list)

        elif type == "article":
            # 🎯 处理"文章"类型的数据
            # 这是知乎专栏文章，不是问题
            cn_type = "专栏"
            
            # 专栏文章数据在target层级中
            zhuanlan = item["target"]
            
            # 提取文章的唯一标识符
            id = zhuanlan["id"]
            
            # 提取文章的标题
            title = zhuanlan["title"]
            
            # 文章URL已经是完整的，直接使用
            url = zhuanlan["url"]
            
            # 将Unix时间戳转换为可读的日期格式(YYYY-MM-DD)
            article_date = datetime.fromtimestamp(zhuanlan["created"]).strftime(
                "%Y-%m-%d"
            )
            
            # 构造数据列表：[类型, ID, 标题, URL, 日期]
            sml_list = [cn_type, id, title, url, article_date]
            
            # 将数据添加到全局问题列表中
            q_list.append(sml_list)

    # 返回下一页的URL，供外部循环继续爬取
    # 如果没有下一页，API会返回空值，循环会自动结束
    return nextUrl
# def save_data(q_list, filename):
#     # 获取绝对路径
#     abs_filename = os.path.abspath(filename)
#     print(f"尝试保存到绝对路径: {abs_filename}")
    
#     # 确保目录存在
#     dir_path = os.path.dirname(abs_filename)
#     if not os.path.exists(dir_path):
#         os.makedirs(dir_path, exist_ok=True)
#         print(f"创建目录: {dir_path}")
#     else:
#         print(f"目录已存在: {dir_path}")

#     df = pd.DataFrame(q_list, columns=["type", "id", "title", "url", "date"])
#     # 根据id去重，并按照时间排序
#     df = df.drop_duplicates(subset=["id"]).sort_values(by="date")

#     # 若文件已存在，则读取原文件，合并后去重，实现文件更新
#     if os.path.exists(abs_filename):
#         try:
#             df_original = pd.read_csv(abs_filename)
#             df = pd.concat([df_original, df], ignore_index=True)
#             df = df.drop_duplicates(subset=["id"]).sort_values(by="date")
#             print(f"合并原有数据，原有{len(df_original)}条")
#         except Exception as e:
#             print(f"读取原文件失败: {e}")

#     try:
#         df.to_csv(abs_filename, index=False, header=True, encoding="utf-8")
#         print(f"✅ 成功保存{len(df)}条数据到: {abs_filename}")
        
#         # 验证文件是否真的存在
#         if os.path.exists(abs_filename):
#             file_size = os.path.getsize(abs_filename)
#             print(f"✅ 文件确认存在，大小: {file_size} bytes")
#         else:
#             print("❌ 警告：文件保存后未找到！")
            
#     except Exception as e:
#         print(f"❌ 保存文件失败: {e}")
#         import traceback
#         traceback.print_exc()



def save_data(q_list, filename):
    """
    💾 保存问题数据到CSV文件
    
    参数:
        q_list: 问题数据列表
        filename: 保存的文件路径
    """
    print(f"🔍 准备保存数据，当前q_list长度: {len(q_list)}")
    
    # 如果q_list为空，直接返回
    if not q_list:
        print("❌ 警告：q_list为空，无法保存数据！")
        return
    
    # 显示前几条数据用于调试
    print(f"📊 数据样例（前3条）:")
    for i, item in enumerate(q_list[:3]):
        print(f"   {i+1}: {item}")

    df = pd.DataFrame(q_list, columns=["type", "id", "title", "url", "date"])
    print(f"📋 DataFrame创建成功，形状: {df.shape}")
    
    # 根据id去重，并按照时间排序
    df = df.drop_duplicates(subset=["id"]).sort_values(by="date")
    print(f"🔄 去重后数据量: {len(df)}")

    # 若文件已存在，则读取原文件，合并后去重，实现文件更新
    if os.path.exists(filename):
        try:
            df_original = pd.read_csv(filename)
            print(f"📁 读取原文件，原有{len(df_original)}条数据")
            df = pd.concat([df_original, df], ignore_index=True)
            df = df.drop_duplicates(subset=["id"]).sort_values(by="date")
            print(f"🔗 合并后数据量: {len(df)}")
        except Exception as e:
            print(f"❌ 读取原文件失败: {e}")

    try:
        df.to_csv(filename, index=False, header=True, encoding="utf-8")
        print(f"✅ 成功保存{len(df)}条数据到{filename}")
        
        # 验证文件
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"✅ 文件确认存在，大小: {file_size} bytes")
        else:
            print("❌ 警告：文件保存后未找到！")
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        import traceback
        traceback.print_exc()

def crawl_1(topicID, q_list):
    """
    🎯 爬取话题的讨论区内容
    
    参数:
        topicID: 话题ID
        q_list: 问题列表，用于存储爬取结果
    """
    # 从Discussion中获取，限制50条
    url = (
        "https://www.zhihu.com/api/v5.1/topics/"
        + topicID
        + "/feeds/essence?offset=0&limit=50"
    )
    while url:
        try:
            text = get_url_text(url)
            if text:  # 确保获取到内容才解析
                url = parseJson(text, q_list)
            else:
                break
        except:
            print(f"目前已有{len(q_list)}条数据")
            break

    url = (
        "https://www.zhihu.com/api/v5.1/topics/"
        + topicID
        + "/feeds/timeline_activity?offset=0&limit=50"
    )
    while url:
        try:
            text = get_url_text(url)
            if text:  # 确保获取到内容才解析
                url = parseJson(text, q_list)
            else:
                break
        except:
            print(f"目前已有{len(q_list)}条数据")
            break

    print("crawl_讨论: 完成")

def crawl_2(topicID, q_list):
    """
    🎯 爬取话题的精华区内容
    
    参数:
        topicID: 话题ID
        q_list: 问题列表，用于存储爬取结果
    """
    # Selected posts 精华
    url = (
        "https://www.zhihu.com/api/v5.1/topics/"
        + topicID
        + "/feeds/top_activity?offset=0&limit=50"
    )
    while url:
        try:
            text = get_url_text(url)
            if text:  # 确保获取到内容才解析
                url = parseJson(text, q_list)
            else:
                break
        except:
            print(f"目前已有{len(q_list)}条数据")
            break
    print("crawl_精华: 完成")

def crawl_3(topicID, q_list):
    """
    🎯 爬取话题的等待回答区内容
    
    参数:
        topicID: 话题ID
        q_list: 问题列表，用于存储爬取结果
    """
    # Awaiting answers 等待回答
    url = (
        "https://www.zhihu.com/api/v5.1/topics/"
        + topicID
        + "/feeds/top_question?offset=0&limit=50"
    )
    while url:
        try:
            text = get_url_text(url)
            if text:  # 确保获取到内容才解析
                url = parseJson(text, q_list)
            else:
                break
        except:
            print(f"目前已有{len(q_list)}条数据")
            break

    url = (
        "https://www.zhihu.com/api/v5.1/topics/"
        + topicID
        + "/feeds/new_question?offset=0&limit=50"
    )
    while url:
        try:
            text = get_url_text(url)
            if text:  # 确保获取到内容才解析
                url = parseJson(text, q_list)
            else:
                break
        except:
            print(f"目前已有{len(q_list)}条数据")
            break

    print("crawl_等待回答: 完成")

if __name__ == "__main__":
    # 漩涡鸣人: 20204759
    # 春野樱: 20135411
    #TODO 指定要爬取的话题ID
    topicID_list = ["19556554"]
    q_list = []

    print(f"当前工作目录: {os.getcwd()}")
    print(f"脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}")

    for topicID in topicID_list:
        print(f"🚀 开始爬取话题ID: {topicID}")
        
        # 传递q_list参数给所有爬取函数
        crawl_1(topicID, q_list)
        crawl_2(topicID, q_list)
        crawl_3(topicID, q_list)
        
        print(f"📊 总共爬取到 {len(q_list)} 条数据")
        
        # 保存数据到CSV文件
        save_data(q_list, 'data/question_list.csv')
