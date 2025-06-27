# # Get All Comments by Question ID

# ### About this script:

# - **Input**: A Question ID
# - **Output**: All Comments of All the answers of the Question, including root comments and child comments
# Last Run: 2024/12/1 23:45


# %%
import re
import os
import json
import time
import pandas as pd
from datetime import datetime
from get_url_text import get_url_text


# %%
def get_answer_id(question_id: str) -> list:
    file_name = f"data/answers_of_question/question_{question_id}.csv"
    if not os.path.exists(file_name):
        print(
            f"问题 {question_id} 数据文件不存在，请先运行 scraping3.py 爬取问题数据。"
        )
        return []
    df = pd.read_csv(file_name)

    return df["a_id"].tolist()


# %%
def parse_root_comment(json_data: dict, answer_id: str) -> list:
    comment_type = "根评论"
    reply_comment_id = ""
    reply_root_comment_id = ""
    comment_id = json_data["id"]
    comment_content = re.sub(r"<.*?>", "", json_data["content"])
    comment_date = datetime.fromtimestamp(json_data["created_time"]).strftime(
        "%Y-%m-%d"
    )
    comment_upvote = json_data["vote_count"]
    child_comment_count = json_data["child_comment_count"]
    author_name = json_data["author"]["member"]["name"]
    author_url_token = json_data["author"]["member"]["url_token"]
    author_gender = json_data["author"]["member"]["gender"]
    author_headline = json_data["author"]["member"]["headline"]

    return [
        answer_id,
        comment_type,
        reply_comment_id,
        reply_root_comment_id,
        comment_id,
        comment_content,
        comment_date,
        comment_upvote,
        child_comment_count,
        author_name,
        author_url_token,
        author_gender,
        author_headline,
    ]


# %%
def get_root_comments(answer_id: str) -> pd.DataFrame:
    try:
        comments_list = []

        url = f"https://www.zhihu.com/api/v4/answers/{answer_id}/root_comments?limit=20&offset=0&order_by=score&status=open"
        text = get_url_text(url)
        json_data = json.loads(text)["data"]
        count = 0

        while json_data:
            for item in json_data:
                root_comment_data = parse_root_comment(item, answer_id)
                comments_list.append(root_comment_data)

            url = json.loads(text)["paging"]["next"]
            text = get_url_text(url)
            json_data = json.loads(text)["data"]
            count += 1

            if count % 30 == 0:
                time.sleep(0.5)
                print(f"评论示例：{root_comment_data[4][:15]}")

        df_comments = pd.DataFrame(
            comments_list,
            columns=[
                "answer_id",
                "comment_type",
                "reply_comment_id",
                "reply_root_comment_id",
                "comment_id",
                "comment_content",
                "comment_date",
                "comment_upvote",
                "child_comment_count",
                "author_name",
                "author_url_token",
                "author_gender",
                "author_headline",
            ],
        )

        return df_comments
    except:
        print(f"获取 {answer_id} 评论失败")
        return None


# %%
def parse_child_comment(json_data: dict, answer_id: str) -> list:
    comment_type = "子评论"
    reply_comment_id = json_data["reply_comment_id"]
    reply_root_comment_id = json_data["reply_root_comment_id"]
    comment_id = json_data["id"]
    comment_content = json_data["content"]
    comment_date = datetime.fromtimestamp(json_data["created_time"]).strftime(
        "%Y-%m-%d"
    )
    comment_upvote = json_data["like_count"]
    child_comment_count = json_data["child_comment_count"]
    author_name = json_data["author"]["name"]
    author_url_token = json_data["author"]["url_token"]
    author_gender = json_data["author"]["gender"]
    author_headline = json_data["author"]["headline"]

    return [
        answer_id,
        comment_type,
        reply_comment_id,
        reply_root_comment_id,
        comment_id,
        comment_content,
        comment_date,
        comment_upvote,
        child_comment_count,
        author_name,
        author_url_token,
        author_gender,
        author_headline,
    ]


# %%
def get_child_comments(comment_item: list) -> pd.DataFrame:
    try:
        answer_id, root_comment_id = comment_item
        comments_list = []

        url = f"https://www.zhihu.com/api/v4/comment_v5/comment/{root_comment_id}/child_comment?limit=20&offset=0"
        text = get_url_text(url)
        json_data = json.loads(text)["data"]
        count = 0

        while json_data:
            for item in json_data:
                root_comment_data = parse_child_comment(item, answer_id)
                comments_list.append(root_comment_data)

            url = json.loads(text)["paging"]["next"]
            text = get_url_text(url)
            json_data = json.loads(text)["data"]
            count += 1

            if count % 30 == 0:
                time.sleep(0.5)
                print(f"评论示例：{root_comment_data[4][:15]}")

        df_comments = pd.DataFrame(
            comments_list,
            columns=[
                "answer_id",
                "comment_type",
                "reply_comment_id",
                "reply_root_comment_id",
                "comment_id",
                "comment_content",
                "comment_date",
                "comment_upvote",
                "child_comment_count",
                "author_name",
                "author_url_token",
                "author_gender",
                "author_headline",
            ],
        )

        return df_comments
    except:
        print(f"获取 {root_comment_id} 子评论失败")
        return None


# %%
def save_data(df_comments: pd.DataFrame, question_id: str) -> None:
    filename = f"data/comments_of_question/question_{question_id}.csv"

    df_tosave = df_comments

    if os.path.exists(filename):
        df_original = pd.read_csv(filename)
        df_tosave = pd.concat([df_original, df_tosave], ignore_index=True)
        df_tosave = df_tosave.drop_duplicates(subset=["comment_id"]).sort_values(
            by="comment_date"
        )
    df_tosave = df_tosave.drop_duplicates(subset=["comment_id"]).sort_values(
        by="comment_date"
    )
    df_tosave.to_csv(filename, index=False, header=True)


# %%
if __name__ == "__main__":
    # 填写要爬取评论的问题 ID
    # 需要提前使用scraping3.py爬取问题信息并保存到data文件夹中，因为要使用问题中的回答 ID
    # 强烈建议一次只运行一个问题，因为爬取评论需要时间较长，容易触发知乎反爬虫机制
    # TODO:
    question_id_list = ["436790259"]
    for question_id in question_id_list:
        answer_id_list = get_answer_id(question_id)
        df_all_comments = pd.DataFrame()

        error_num = 0
        for i, answer_id in enumerate(answer_id_list):
            df_root_comments = get_root_comments(answer_id)

            if df_root_comments is None:
                error_num += 1
            else:
                error_num = 0
                df_all_comments = pd.concat([df_all_comments, df_root_comments])
                save_data(df_all_comments, question_id)
            if error_num > 5:
                print(f"⚠️⚠️⚠️需要填写验证码⚠️⚠️⚠️")
                break

            if i % 30 == 0:
                time.sleep(0.5)

        comment_item_list = df_all_comments[df_all_comments["child_comment_count"] > 0][
            ["answer_id", "comment_id"]
        ].values.tolist()

        for i, comment_item in enumerate(comment_item_list):
            df_child_comments = get_child_comments(comment_item)

            if df_child_comments is None:
                error_num += 1
            else:
                error_num = 0
                df_all_comments = pd.concat([df_all_comments, df_child_comments])

            if error_num > 5:
                print(f"⚠️⚠️⚠️需要填写验证码⚠️⚠️⚠️")
                break

            if i % 30 == 0:
                time.sleep(0.5)
                save_data(df_all_comments, question_id)

        save_data(df_all_comments, question_id)
        print(f"问题 {question_id} 评论数据已保存。")
    print("所有问题评论数据已保存。")
