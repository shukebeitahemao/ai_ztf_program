# Please install OpenAI SDK first: `pip3 install openai`
from openai import OpenAI
import sys
import time

GET_KG_PROMPT = prompt.GET_KG_PROMPT
print(GET_KG_PROMPT)
# def start_ds_client():
#     print("正在初始化API客户端...")
#     try:
#         client = OpenAI(api_key="sk-9263361d03dc4c2dad81f483bf3185df", base_url="https://api.deepseek.com")
#         print("API客户端初始化成功")
#         return client
#     except Exception as e:
#         print(f"API客户端初始化失败: {str(e)}", file=sys.stderr)
#         sys.exit(1)

# def get_kg_json_by_txt(client,txt,prompt)
# print("正在发送API请求...")
# try:
#     start_time = time.time()
#     response = client.chat.completions.create(
#         model="deepseek-reasoner",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant"},
#             {"role": "user", "content": }
#         ],
#         stream=False,
#         # timeout=30  # 设置30秒超时
#     )
#     end_time = time.time()
#     print(f"API请求耗时: {end_time - start_time:.2f}秒")
    
#     print("正在处理API响应...")
#     print(response.choices[0].message.content)
# except Exception as e:
#     print(f"发生错误: {str(e)}", file=sys.stderr)
#     sys.exit(1)