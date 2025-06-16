from util.chat_util import (
    initialize_llamaindex,
    get_user_keywords,
    get_es_docs,
    find_paragraphs_with_keyword,
    get_paras_from_kws
)
from util import db_util
import uuid
import json
# 初始化llm和embed模型
llm, embed_model = initialize_llamaindex(deepseekapi="sk-1ce00a653d2c46238249e685eb3a9c7d")
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

client = OpenAI(api_key="sk-1ce00a653d2c46238249e685eb3a9c7d", base_url="https://api.deepseek.com")
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
    user_msg: str = Query(..., description="用户消息"),
    story_type: str = Query(..., description="故事类型")
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
    print('调用chat后的msg_pool',msg_pool)
    print('调用chat后的当前用户msg_list',msg_list)
    return {'sessionid':sessionid,'system_msg':system_msg}

@app.get("/load_history")
def load_history(
    userid: str = Query(..., description="用户ID")
):
    excute_query = f"""
    SELECT session_id,update_time,abstract FROM message WHERE user_id = '{userid}' ;
    """
    history = db_util.execute_query(excute_query)
    formatted_history = []
    for session_id, update_time, abstract in history:
        formatted_history.append({
            'session_id': session_id,
            'abstract': abstract,
            'update_time': update_time.strftime('%Y/%m/%d %H:%M:%S')
        })
    print('load_history',formatted_history)
    #此时只加载用户历史记录，但是不加入msg_pool，等到用户前端点击某条历史记录，或者创造新的聊天记录时才加入msg_pool
    
    return {"msg": formatted_history}

@app.get("/load_specific_session")
def load_specific_session(
    userid: str = Query(..., description="用户ID"),
    sessionid: str = Query(..., description="会话ID")
):
    excute_query = f"""
    SELECT user_id,session_id,history FROM message WHERE user_id = '{userid}' AND session_id = '{sessionid}';
    """
    history = db_util.execute_query(excute_query)
    formatted_history = []
    for user_id, session_id, history in history:
        formatted_history.append({
            'user_id': user_id,
            'session_id': session_id,
            'history': history
        })
    if formatted_history:
        history_data = formatted_history[0]['history']
        if isinstance(history_data, str):
            history_data = json.loads(history_data)
        if userid not in msg_pool:
            msg_pool[userid] = {}
        if sessionid not in msg_pool[userid]:
            msg_pool[userid][sessionid] = []
        msg_pool[userid][sessionid] = history_data
        print('加载了特定旧历史记录后的msg_pool',msg_pool)
    return {"msg": formatted_history}

@app.get("/create_user")
def create_user():
    user_id = str(uuid.uuid4())
    session_id = 'session_'+str(uuid.uuid4())
    excute_query = f"""
    INSERT INTO message (user_id, session_id) VALUES ('{user_id}', '{session_id}');
    """
    db_util.execute_query(excute_query)
    msg_pool[user_id] = {session_id: []}
    print('创建了新用户后的msg_pool',msg_pool)
    return {"user_id": user_id, "session_id": session_id}

@app.get("/create_new_chat")
def create_new_chat(
    userid: str = Query(..., description="用户ID")
):
    session_id = 'session_'+str(uuid.uuid4())
    excute_query = f"""
    INSERT INTO message (user_id, session_id) VALUES ('{userid}', '{session_id}');
    """
    db_util.execute_query(excute_query)
    msg_pool[userid] = {session_id: []}
    print('创建了新会话后的msg_pool',msg_pool)
    return {"user_id": userid, "session_id": session_id}

@app.get("/chat/delete_session")
def delete_session(
    userid: str = Query(..., description="用户ID"),
    sessionid: str = Query(..., description="会话ID")
):
    del msg_pool[userid][sessionid]
    print('删除会话后的msg_pool',msg_pool)
    return {"msg": "删除成功"}

@app.get("/chat/save_usermsg")
def save_usermsg(
    userid: str = Query(..., description="用户ID")
):
    # 获取该用户的所有会话消息
    user_sessions = msg_pool.get(userid, {})    
    for session_id, history in user_sessions.items():
        # 将历史记录转换为JSON字符串
        history_json = json.dumps(history, ensure_ascii=False)
        print('history_json',history_json)
        GET_ABSTRCT_PROMPT = f"""
        你是一个历史学家，擅长从历史人物的对话中提取关键词，并根据关键词生成摘要。
        用户的历史对话是：
        {history}
        请根据用户的历史对话，提取关键词，并根据关键词生成摘要。
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": GET_ABSTRCT_PROMPT},],
            stream=False
        )
        abstract = response.choices[0].message.content
        print('abstract',abstract)
        # 更新数据库中的历史记录
        update_query = f"""
        UPDATE message 
        SET history = '{history_json}',
            update_time = CURRENT_TIMESTAMP,
            abstract = '{abstract}'
        WHERE user_id = '{userid}' 
        AND session_id = '{session_id}';
        """
        db_util.execute_query(update_query)
    return {"msg": "保存成功"}



