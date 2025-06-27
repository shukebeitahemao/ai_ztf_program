import os
import time
import pandas as pd
from bs4 import BeautifulSoup as bs  # HTML解析库，用于从网页中提取数据
from get_url_text import get_url_text  # 自定义的网络请求模块
import random
#利用playwrigrt获取登陆cookie


# 处理热榜数







#这部分代码用于根据问题列表爬取问题的元信息。
# 可从问题/专栏列表中读取并筛选出符合条件（如非 “专栏” 类型且在指定日期之后）的问题 ID 列表，
# 并爬取这些问题的元数据。
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
    df = pd.read_csv(filename)
    
    # 筛选条件1：排除专栏文章，只保留问题和回答
    df = df[df["type"] != "专栏"]
    
    # 筛选条件2：只爬取指定日期之后的问题（可根据需要修改）
    df = df[df["date"] >= "2024-10-14"]
    
    # 转换为列表格式，方便后续处理
    q_list = df.values.tolist()
    return q_list

def get_question_data(html_text):
    """
    🔍 从HTML页面中解析问题的元数据
    
    参数：
        html_text: 问题详情页的HTML源码
    
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

        qContent = bsobj.find_all("meta", attrs={"itemprop": "name"})[0]["content"]
        followerCount = bsobj.find_all("strong", attrs={"class": "NumberBoard-itemValue"})[0]["title"]
        viewCount = bsobj.find_all("strong", attrs={"class": "NumberBoard-itemValue"})[1]["title"]
        answerCount = bsobj.find_all("meta", attrs={"itemprop": "answerCount"})[0]["content"]
        topicTag = bsobj.find_all("meta", attrs={"itemprop": "keywords"})[0]["content"]
        date = bsobj.find_all("meta", attrs={"itemprop": "dateCreated"})[0]["content"]

        return [q_id, qContent, followerCount, viewCount, answerCount, topicTag, date[:10]]

    except:
        print("Unknown Error !")
        return [
            q_id,
            "UnknownError",
            "UnknownError",
            "UnknownError",
            "UnknownError",
            "UnknownError",
            "UnknownError",
        ]

def save_data(q_info_list, filename):
    """
    💾 保存问题元数据到CSV文件
    
    参数：
        q_info_list: 问题信息列表
        filename: 输出文件名（通常是question_meta_info.csv）
    
    数据处理逻辑：
        1. 创建DataFrame并设置列名
        2. 如果文件已存在，则合并新旧数据
        3. 清理无效数据（UnknownError）
        4. 按问题ID去重，保留最新数据
        5. 格式化日期并排序
        6. 保存到CSV文件
    """
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
    
    # 如果文件已经存在，合并新旧数据
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df = pd.concat([df_old, df], ignore_index=True)
        
        # 数据清理：删除解析失败的问题（标记为UnknownError的记录）
        df = df[df["q_content"] != "UnknownError"]
        
        # 按问题ID去重，保留最新的数据
        df = df.drop_duplicates(subset=["q_id"], keep="last")
        
        # 日期格式化：将"-"替换为"/"
        df["created_date"] = df["created_date"].str.replace("-", "/")
        df["created_date"] = pd.to_datetime(df["created_date"])
        
        # 按创建日期排序
        df = df.sort_values(by=["created_date"])
        
        # 保存到CSV文件，使用UTF-8编码以支持中文
        df.to_csv(filename, index=False, header=True, encoding="utf-8")
#TODO 指定问题列表
q_list = get_question_list("data/question_list.csv")
print(f"共{len(q_list)}个问题")
q_info_list = []

#TODO 可设置开始和结束位置，用于在出错中断时重新爬取
for i, item in enumerate(q_list[:]):
    #实际上只用到了id列，其他列可以忽略
    q_id = item[1]

    url = f"https://www.zhihu.com/question/{str(q_id)}"
    text = get_url_text(url)
    q_info = get_question_data(text)
    q_info_list.append(q_info)

    if i % 30 == 0:
        print(q_info[1])
        save_data(q_info_list, "data/question_meta_info.csv")
        q_info_list = []
        time.sleep(random.uniform(0, 2))
        print(f"已保存{i+1}条数据")

save_data(q_info_list, "data/question_meta_info.csv")

