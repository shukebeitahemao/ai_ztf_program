from util.chat_util import (
    initialize_llamaindex,
    get_user_keywords,
    get_es_docs,
    find_paragraphs_with_keyword,
    get_paras_from_kws
)
from util import db_util

# 初始化llm和embed模型
llm, embed_model = initialize_llamaindex(deepseekapi="sk-5f2880952eb543a59d02d1015dcdd8e1")
summary_index,simple_index = db_util.load_indexes()
# chat_history = [
#     {"role": "assistant", "content": "你好"},
#     {"role": "user", "content": "邹韬奋是谁？"},
#     {"role": "assistant", "content": "他是一个伟大的作家"},
#     {"role": "user", "content": "他在监狱里面经历了什么？"},

# ]
  

from fastapi import FastAPI, Query
from typing import Optional
from openai import OpenAI
app = FastAPI()

client = OpenAI(api_key="sk-5f2880952eb543a59d02d1015dcdd8e1", base_url="https://api.deepseek.com")
msg_pool = {
    'user1':{'session1':[{"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"}],
        'session2':[{"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"}]
    },
    'user2':{'session1':[{"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"}],
        'session2':[{"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"}]
    }
    
}
@app.get("/chat")
def chat(
    userid: str = Query(..., description="用户ID"),
    sessionid: str = Query(..., description="会话ID"), 
    user_msg: str = Query(..., description="用户消息")
):
    #获取msg_pool中user_id和seession_id对应的msg列表
    msg_list = msg_pool[userid][sessionid]
    msg_list.append({"role": "user", "content": user_msg})
    ######根据关键词查询的信息，渲染为关键词模板,可能会出错
    try:
        an_kw = get_user_keywords(msg_list)
        # 处理 get_user_keywords 的结果，避免 "Expression value is unused" 错误
        if an_kw.get('is_about_ztaofen'):
            kws = an_kw['keywords']
            kw_paragraphs_list = get_paras_from_kws(kws)
        #循环写入prompt
        KW_PARA_PROMPT = """"""
        for ky,kw_paragraphs in zip(kws,kw_paragraphs_list):
            KW_PARA_PROMPT += f"用户的关键词是'{ky}'，\n相关段落是:{kw_paragraphs}\n\n"
    except Exception as e:  
        KW_PARA_PROMPT = ""
    #######根据语义去向量数据库查询的信息
    res = db_util.get_final_nodes_text(summary_index,simple_index,user_query=user_msg)
    #######制作模板
    GET_AI_ANSWER=f"""
    你要扮演我国历史上的著名人物邹韬奋和用户进行对话。
    你们已经进行了如下对话:
    {msg_list}
    当前的用户发言是：
    {user_msg}
    从用户发言中提取的关键词以及从数据库中抽取的该关键词相关文档是：
    {KW_PARA_PROMPT}
    你还可以参考如下信息：
    {res}
    请给出对用户合适的回应：
"""
    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": GET_AI_ANSWER},
    ],
    stream=False
    )
    system_msg = response.choices[0].message.content
    msg_list.append({"role": "system", "content":"{system_msg}".format(system_msg=system_msg)})
    msg_pool[userid][sessionid] = msg_list
    with open('temp.txt', 'w', encoding='utf-8') as f:
        f.write(str(msg_list))
    return {'sessionid':sessionid,'system_msg':system_msg}

