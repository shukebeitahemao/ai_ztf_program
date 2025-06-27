"""
知乎爬虫 - 第五步：根据用户ID获取作者详细信息
=========================================

🎯 功能说明：
- 输入：用户token列表（由scraping4.5生成）
- 输出：每个用户的详细信息（粉丝数、获赞数、徽章等）
- 用途：获取回答者的详细资料，用于用户画像分析

📊 获取的用户信息：
- 基本信息：用户名、性别、IP地址
- 统计数据：获赞数、被感谢数、粉丝数、被收藏数
- 创作数据：回答数+文章数
- 认证信息：VIP状态、身份认证、优秀回答者等徽章

🚀 数据来源：
- 用户主页HTML中的JavaScript初始化数据
- 解析JSON格式的用户完整信息

⚠️ 注意事项：
- 需要先运行 scraping4.5 生成用户token列表
- 容易触发验证码，需要定期更新cookie
- 连续失败5次会自动停止
- 支持断点续爬（自动跳过已爬取的用户）

上次运行：2024/11/16 15:05
"""

import os
import time
import json
import pandas as pd
from bs4 import BeautifulSoup as bs
from get_url_text import get_url_text

def get_tokens(sourse_filename, data_store_file):
    # sourse_filename: scraping3.5_data_processing.py output
    # data_store_file: output file name
    # Import csv, convert to list
    df = pd.read_csv(sourse_filename, header=None)
    token_list = df.iloc[:, 0].tolist()
    print(f"Total {len(token_list)} users")

    if not os.path.exists(data_store_file):
        a = pd.DataFrame(
            [],
            columns=[
                "user_token",
                "name",
                "gender",
                "IP_address",
                "voteupCount",
                "thankedCount",
                "followerCount",
                "favoritedCount",
                "productCount",
                "VIPs",
                "identity",
                "top_writer",
            ],
        )
        a.to_csv(data_store_file, index=False, header=True)
        print(f"Create new file: {data_store_file}")
    else:
        df_exist = pd.read_csv(data_store_file)
        token_exist = df_exist["user_token"].tolist()
        token_list = list(set(token_list) - set(token_exist))

    print(f"Find {len(token_list)} new users")
    return token_list

def get_author_info(user_text, token):
    try:
        json_text = bs(user_text, "html.parser").find("script", attrs={"id": "js-initialData"}).text
        json_data = json.loads(json_text)["initialState"]["entities"]["users"][token]

        token = json_data["urlToken"]
        name = json_data["name"]
        gender = json_data["gender"]
        IP_address = json_data["ipInfo"][5:]
        voteupCount = json_data["voteupCount"]
        thankedCount = json_data["thankedCount"]
        followerCount = json_data["followerCount"]
        favoritedCount = json_data["favoritedCount"]
        productCount = json_data["answerCount"] + json_data["articlesCount"]
        VIPs = json_data["vipInfo"]["isVip"] + json_data["kvipInfo"]["isVip"]
        badge_info = json_data["badgeV2"]["mergedBadges"]
        identity = 1 if "identity" in [badge["type"] for badge in badge_info] else 0
        top_writer = 1 if "best" in [badge["type"] for badge in badge_info] else 0

        return [
            token, # 用户token
            name, # 用户名
            gender, # 性别
            IP_address, # IP地址
            voteupCount, # 总获赞数
            thankedCount, # 被喜欢数
            followerCount, # 粉丝数
            favoritedCount, # 被收藏数
            productCount, # 回答数+文章数
            VIPs, # 拥有几项VIP
            identity, # 是否拥有identity徽章
            top_writer, # 是否拥有best徽章
        ]
    except:
        print(f"{token} Text Error !")
        return None

def save_data(user_info_list, filename):
    df = pd.DataFrame(
        user_info_list,
        columns=[
            "user_token",
            "name",
            "gender",
            "IP_address",
            "voteupCount",
            "thankedCount",
            "followerCount",
            "favoritedCount",
            "productCount",
            "VIPs",
            "identity",
            "top_writer",
        ],
    )

    df.to_csv(filename, index=False, mode="a", header=False)

# RUN `scraping3.5_data_processing.py` FIRST!
# 知乎乱码不会影响获取用户信息

if __name__ == "__main__":
    #TODO: 输入文件名
    token_list = get_tokens(
        sourse_filename="data/user_tokens.csv", 
        data_store_file="data/author_meta_info.csv"
    )
    user_info_list = []

    error_num = 0
    for i, token in enumerate(token_list):
        if token:
            url = f"https://www.zhihu.com/people/{str(token)}"
            user_text = get_url_text(url)

            if user_text and ("该账号已" in user_text or "该用户已" in user_text):
                user_info = [token] + ["None"] * 11
                user_info_list.append(user_info)
                save_data(user_info_list, "data/author_meta_info.csv")
                user_info_list = []
                print(f"⚠️⚠️⚠️{token}已被封禁⚠️⚠️⚠️")
                continue

            user_info = get_author_info(user_text, token)

            if user_info:
                error_num = 0
                user_info_list.append(user_info)
            else:
                error_num += 1  # 判断连续错误，达到5个时认为出现验证码错误

        if error_num >= 5:
            print(f"⚠️⚠️⚠️需要填写验证码并重新运行⚠️⚠️⚠️")
            break

        if i % 30 == 0:
            time.sleep(0.5)
            save_data(user_info_list, "data/author_meta_info.csv")
            user_info_list = []

    save_data(user_info_list, "data/author_meta_info.csv")

    print("Finish!")
