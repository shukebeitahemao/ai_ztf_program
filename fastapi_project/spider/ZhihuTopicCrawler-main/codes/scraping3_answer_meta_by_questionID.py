"""
知乎爬虫 - 第三步：根据问题ID获取所有回答的详细信息
===============================================

🎯 功能说明：
- 输入：问题ID列表
- 输出：每个问题下所有回答的详细信息
- 用途：获取回答内容、作者信息、点赞数、评论数等详细数据

📊 数据流程：
1. 读取 question_meta_info.csv（由scraping2生成）
2. 对每个问题调用知乎API获取回答列表
3. 解析JSON数据提取回答详情和作者信息
4. 保存到 data/answers_of_question/question_{问题ID}.csv

🚀 核心API：
- https://www.zhihu.com/api/v4/questions/{问题ID}/feeds
- 支持分页获取所有回答
- 包含作者详细信息和回答统计数据

⚠️ 注意事项：
- 需要先运行 scraping2 获取问题元数据
- 爬取时间较长，支持断点续爬
- 会触发验证码机制，需要定期更新cookie

上次运行：2024/11/16 12:55
"""

import re  # 正则表达式，用于清理HTML标签
import os
import json  # 处理API返回的JSON数据
import time
import pandas as pd
from datetime import datetime  # 时间戳转换
from get_url_text import get_url_text  # 自定义的网络请求模块

def get_q_list(filename):
    df = pd.read_csv(filename, encoding="utf-8")
    df = df[df["answerCount"] > 5]  # 默认爬取回答数大于5的问题
    df = df[df["created_date"] >= "2024-10-15"]  # 可选要更新的问题的时间范围
    q_list = df.values.tolist()
    print(f"共有 {len(q_list)} 个回答数大于5且不重复的问题")

    return q_list[::-1]  # 从后往前爬

def parse_data(html, q_id):

    json_data = json.loads(html)["data"]
    next_url = json.loads(html)["paging"]["next"]
    is_end = json.loads(html)["paging"]["is_end"]

    one_q_all_answer = []

    try:
        for item in json_data:
            one_answer_list = []

            question_id = q_id  # Question id
            answer_content = item["target"]["content"]
            answer_content = re.sub("<[^<]+?>", "", answer_content)
            answer_date = datetime.fromtimestamp(item["target"]["created_time"]).strftime(
                "%Y-%m-%d"
            )  # Answer date
            answer_upvote = item["target"]["voteup_count"]  # upvote count
            answer_comment = item["target"]["comment_count"]  # comment count
            answer_id = item["target"]["id"]  # answer ID
            author_name = item["target"]["author"]["name"]  # author name
            author_gender = item["target"]["author"][
                "gender"
            ]  # author gender, 1 male 2 female
            author_url_token = item["target"]["author"]["url_token"]  # author ID
            author_follower_count = item["target"]["author"][
                "follower_count"
            ]  # author follower count
            author_headline = item["target"]["author"]["headline"]  # author bio

            one_answer_list = [
                question_id,
                answer_content,
                answer_date,
                answer_upvote,
                answer_comment,
                answer_id,
                author_name,
                author_gender,
                author_url_token,
                author_follower_count,
                author_headline,
            ]
            one_q_all_answer.append(one_answer_list)

        return one_q_all_answer, next_url, is_end

    except Exception as e:
        print(one_q_all_answer)
        print(e)

def save_data(answer_info, q_id):

    filename = f"data/answers_of_question/question_{str(q_id)}.csv"

    df = pd.DataFrame(
        answer_info,
        columns=[
            "q_id",
            "a_content",
            "a_date",
            "a_upvote",
            "a_comment",
            "a_id",
            "au_name",
            "au_gender",
            "au_urltoken",
            "au_followerCount",
            "au_headline",
        ],
    )
    if os.path.exists(filename):
        df_original = pd.read_csv(filename)
        df = pd.concat([df_original, df], ignore_index=True)
        df = df.drop_duplicates(subset=["a_id"]).sort_values(by="a_date")

    df.to_csv(filename, index=False, header=True)

if __name__ == "__main__":
    # TODO: 指定问题列表
    q_list = get_q_list("data/question_meta_info.csv")
    # 也可手动输入问题 ID 以获取回答数据
    # q_list = ["291278869", "291278870"]

    # 爬一段时间会触发知乎的验证码机制导致HTTPError报错，需要手动重新设置开始位置
    begin_index = 0  # 将发生报错的问题序号更新到这里即可
    for i, item in enumerate(q_list[begin_index:]):  
        q_id = item[0]

        print(f"\nquestion {i+begin_index} {item[1]} Begin, qid: {q_id}")

        url = f"https://www.zhihu.com/api/v4/questions/{str(q_id)}/feeds?include=content%2Cauthor.follower_count"

        if_question_exist = os.path.exists(f"data/answers_of_question/question_{str(q_id)}.csv")
        get_data_by_time = False # 爬虫中是否按时间排序

        # ⚠️⚠️⚠️若按时间排序更新数据中发生报错，则需要删除该问题的对应的CSV文件，重新爬取⚠️⚠️

        if if_question_exist:
            data_existing = pd.read_csv(f"data/answers_of_question/question_{str(q_id)}.csv")
            a_id_existing = data_existing["a_id"].values.tolist()

            try:
                # 已有数据的旧问题尝试按时间排序，节省时间
                text = get_url_text(url + "&order=updated")
                data, url, is_end = parse_data(text, q_id)
                url = url + "&order=updated"
                get_data_by_time = True
            except:
                # 若不能按时间排序，则按默认顺序
                pass

        # 对于回答数很多的问题，报错时可在此处添加中途url，方便断点续爬
        # url = "" # 放入报错前最后输出的url
        #TODO

        page = 0
        is_end = False
        while not is_end:
            text = get_url_text(url)
            data, url, is_end = parse_data(text, q_id)

            save_data(data, q_id)

            if get_data_by_time:
                # 按时间排序时，若所有数据都已爬取，跳出循环，更新完成
                a_id = [item[5] for item in data]
                if all(item in a_id_existing for item in a_id):
                    break

            page += 1
            if page % 10 == 0:
                time.sleep(0.5)
                try:
                    print(url)
                    print(f"文本示例：{data[-1][1][:15]}")
                except:
                    pass

        print(f"\nquestion {i+begin_index} {item[1]} Finish")

    print("Finish!!")
