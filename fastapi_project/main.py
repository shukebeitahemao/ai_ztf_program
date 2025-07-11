from fastapi_project.util.chat_util import (
    initialize_llamaindex,
    get_user_keywords,
    get_es_docs,
    find_paragraphs_with_keyword,
    get_paras_from_kws
)
import asyncio
from fastapi_project.util.db_util import get_docs_from_summaryindex
from fastapi_project.settings import settings
from fastapi_project.util import db_util
from fastapi_project.util.speech_recognition import recognize_audio_file
from fastapi_project.util.text_to_speech import synthesize_text
from fastapi_project.util.spider_util import get_baidu_hot_news,get_topics,save_to_db
import uuid
import json
from llama_index.core import StorageContext, get_response_synthesizer, load_index_from_storage
# 初始化llm和embed模型 - 只调用一次
llm, embed_model = initialize_llamaindex(deepseekapi=settings.DEEPSEEK_API)
# 加载索引时使用已初始化的模型
summary_index,simple_index = db_util.load_indexes()
# chat_history = [
#     {"role": "assistant", "content": "你好"},
#     {"role": "user", "content": "邹韬奋是谁？"},
#     {"role": "assistant", "content": "他是一个伟大的作家"},
#     {"role": "user", "content": "他在监狱里面经历了什么？"},

# ]
#加载新闻索引
storage_context = StorageContext.from_defaults(persist_dir="fastapi_project\\store\\news_summaryindex")
loaded_news_sum_index = load_index_from_storage(storage_context)
  

from fastapi import FastAPI, Query, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from openai import OpenAI
import os
from datetime import datetime
app = FastAPI()
# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    # 允许的源列表
    #allow_origins=["http://localhost:5173"],  # 替换成您的前端URL
    # 或者在开发环境中允许所有源
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

client = OpenAI(api_key=settings.DEEPSEEK_API, base_url="https://api.deepseek.com")
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

#get_docs_from_summaryindex(loaded_news_sum_index)

@app.get("/generate_topic_and_comments")
async def generate_topic_and_comments():
    """
    进行爬虫、入库、选择最新热点，调取index、产生时评
    """
    #1.爬虫和入库
    news_text = get_baidu_hot_news()
    # 过滤掉空列表的情况
    filtered_news_text = {key: value for key, value in news_text.items() if value}
    res = get_topics(filtered_news_text)
    save_to_db(res,filtered_news_text)
    #2.从数据库取出最新热点数据
    query = """
    select * from(
select distinct on(content_length)* from(
SELECT * FROM baidu_news 
WHERE DATE_TRUNC('minute', created_at) = (
    SELECT MAX(DATE_TRUNC('minute', created_at)) FROM baidu_news
) and content_length > 100) as result) as b
order by  hottopic;
    """
    res = db_util.execute_query(query)
    import pandas as pd
    df = pd.DataFrame(res)
    groups = df.groupby(by=[1])
    titles=[]
    abstracts=[]
    keywords_list=[]
    contexts=[]
    for name,group in groups:
        titles.append(group.iloc[0][1])
        abstracts.append(group.iloc[0][9])
        keywords_list.append(group.iloc[0][10])
        context = ''
        for cont in group.iloc[:,3]:
            context +='报道：\n\n'+ cont + '\n'+'------------------------------------\n'
        contexts.append(context)
    df_news=pd.DataFrame({'title':titles,'abstract':abstracts,'keywords':keywords_list,'context':contexts})
    print(df_news['keywords'][0])
    llm, embed_model = initialize_llamaindex(deepseekapi=settings.DEEPSEEK_API)
    #加载新闻索引
    storage_context = StorageContext.from_defaults(persist_dir="fastapi_project\\store\\news_summaryindex")
    loaded_news_sum_index = load_index_from_storage(storage_context)
    # 检索
    ref_source = []
    for keywords in df_news['keywords']:
        query = f"""
        用户希望查询的主题是：{keywords},
        哪些文档的主题和用户查询的主题相符合？
        """
        ref_docs = get_docs_from_summaryindex(loaded_news_sum_index,query=query,k=3)
        # 选择text最长的ref_doc
        ref_doc = max(ref_docs, key=lambda x: len(x['text'])) if ref_docs else None
        ref_source.append(ref_doc['text'])
    df_news['ref_resource'] = ref_source
    #开始获取评论
    print(len(df_news))
    from openai import OpenAI
    client = OpenAI(api_key=settings.DEEPSEEK_API, base_url="https://api.deepseek.com")
    system_msg_list = []
    one_comment_list = []
    for i in range(len(df_news)):
        se = df_news.iloc[i]
        context = se['context']
        ref_resource= se['ref_resource']
        GET_COMMENTS_PROMPT=f"""
        任务：你将扮演邹韬奋对时事新闻进行评论。你需要参考时事新闻的相关报道，并模仿目标文本纂写评论。
        评论的长度和目标文本类似。
        注意：
        1.你需要解析目标文本所使用的叙述结构、修辞手法和语言风格，以及重要的态度，并在评论中体现这些特点。
        2.你需要围绕时事新闻进行评论，而不能超出给定的时事新闻的范围。
        3.最大限度利用时事新闻的信息。
        4.你需要尽可能改写目标文本中的描述，以适应对时事新闻的评论。
        ==============================
        你参考的时事新闻是：
        {context}
        ===============================
        你需要仿照的目标文本是：
        {ref_resource}
        ===============================
        你的评论：
        """
        response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": GET_COMMENTS_PROMPT},
        ],
        stream=False
        )
        system_msg = response.choices[0].message.content
        system_msg_list.append(system_msg)
        GET_ONE_COMMENT_PROMPT = f"""
        你将扮演邹韬奋，依据下列评论文本，总结评论内容，形成一句掷地有声的概括性评论。
        概括性评论需要吸人眼球，具有口语特征，不要使用书面语的特殊用法。不超过20个字，仅返回概括性评论内容，不需要附加其余的解释，不要含有双引号，不要含有冒号。
        评论文本是：
        {system_msg}
        你的评论：
        """
        response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": GET_ONE_COMMENT_PROMPT},
        ],
        stream=False
        )
        one_comment = response.choices[0].message.content
        one_comment_list.append(one_comment)
    df_news['comments'] = system_msg_list
    df_news['one_comment'] = one_comment_list
    return_msg = df_news.loc[:,['title','one_comment','abstract','comments','keywords','ref_resource']]
    return {'msg':return_msg}









@app.get("/chat")
def chat(
    userid: str = Query(..., description="用户ID"),
    sessionid: str = Query(..., description="会话ID"), 
    user_msg: str = Query(..., description="用户消息"),
    story_type: str = Query(..., description="故事类型"),
    func_control: dict = Form(default={'Vector': True, 'knowledge': True, 'EsSearch': True, 'Model_enhance': True})
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



# @app.get("/chat")
# def chat(
#     userid: str = Query(..., description="用户ID"),
#     sessionid: str = Query(..., description="会话ID"), 
#     user_msg: str = Query(..., description="用户消息"),
#     story_type: str = Query(..., description="故事类型")
# ):
#     #获取msg_pool中user_id和seession_id对应的msg列表
#     msg_list = msg_pool[userid][sessionid]
#     msg_list.append({"role": "user", "content": user_msg})
#     ######根据关键词查询的信息，渲染为关键词模板,可能会出错
#     try:
#         an_kw = get_user_keywords(msg_list)
#         # 处理 get_user_keywords 的结果，避免 "Expression value is unused" 错误
#         if an_kw.get('is_about_ztaofen'):
#             kws = an_kw['keywords']
#             kw_paragraphs_list = get_paras_from_kws(kws)
#         #循环写入prompt
#         KW_PARA_PROMPT = """"""
#         for ky,kw_paragraphs in zip(kws,kw_paragraphs_list):
#             KW_PARA_PROMPT += f"用户的关键词是'{ky}'，\n相关段落是:{kw_paragraphs}\n\n"
#     except Exception as e:  
#         KW_PARA_PROMPT = ""
#     #######根据语义去向量数据库查询的信息
#     res = db_util.get_final_nodes_text(summary_index,simple_index,user_query=user_msg)
#     #######制作模板
#     GET_AI_ANSWER=f"""
#     你要扮演我国历史上的著名人物邹韬奋和用户进行对话。
#     你们已经进行了如下对话:
#     {msg_list}
#     当前的用户发言是：
#     {user_msg}
#     从用户发言中提取的关键词以及从数据库中抽取的该关键词相关文档是：
#     {KW_PARA_PROMPT}
#     你还可以参考如下信息：
#     {res}
#     请给出对用户合适的回应，回复中不需要加入动作或神情描述，只需要给出当事人的语言回复：
# """
#     response = client.chat.completions.create(
#     model="deepseek-chat",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": GET_AI_ANSWER},
#     ],
#     stream=False
#     )
#     system_msg = response.choices[0].message.content
#     msg_list.append({"role": "system", "content":"{system_msg}".format(system_msg=system_msg)})
#     msg_pool[userid][sessionid] = msg_list
#     with open('temp.txt', 'w', encoding='utf-8') as f:
#         f.write(str(msg_list))
#     print('调用chat后的msg_pool',msg_pool)
#     print('调用chat后的当前用户msg_list',msg_list)
    
#     # 生成语音
#     audio_data = None
#     audio_duration = 0
#     try:
#         if system_msg:  # 确保system_msg不为None
#             tts_result = synthesize_text(system_msg, voice="longwan")
#             if tts_result:
#                 audio_data, audio_duration = tts_result
#                 print(f"语音合成成功，时长: {audio_duration}秒")
#     except Exception as e:
#         print(f"语音合成失败: {e}")
    
#     return {
#         'sessionid': sessionid,
#         'system_msg': system_msg,
#         'audio_data': audio_data,
#         'audio_duration': audio_duration
#     }

@app.get("/load_history")
def load_history(
    userid: str = Query(..., description="用户ID")
):
    excute_query = f"""
    SELECT session_id,update_time,abstract FROM message WHERE user_id = '{userid}' ;
    """
    history = db_util.execute_query(excute_query)
    # print('没有历史数据的情况',history)
    if not history:
        return {"msg": [{'session_id':10001,'abstrc':'10001','update_time':'1999/01/01 12:00:00'}]}
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
    if history:
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
    #只需要返回用户id，不需要写入数据库，等到用户离开的时候自然会写入，除非用户没有聊天
    # excute_query = f"""
    # INSERT INTO message (user_id, session_id) VALUES ('{user_id}', '{session_id}');
    # """
    # db_util.execute_query(excute_query)
    msg_pool[user_id] = {session_id: []}
    print('创建了新用户后的msg_pool',msg_pool)
    return {"user_id": user_id}

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
    #deletesession就是从列表删除，但是在create_new_chat中会重新创建一个会话,所以可能会要求删除内存中的会话
    if userid in msg_pool and sessionid in msg_pool[userid]:
        del msg_pool[userid][sessionid]
    print('删除会话后的msg_pool',msg_pool)
    #删除数据库中的会话
    excute_query = f"""
    DELETE FROM message WHERE user_id = '{userid}' AND session_id = '{sessionid}';
    """
    db_util.execute_query(excute_query)
    return {"msg": "删除成功"}

@app.get("/chat/save_usermsg")
def save_usermsg(
    userid: str = Query(..., description="用户ID")
):
    # 获取该用户的所有会话消息，如果用户没有聊天，则不保存
    if userid not in msg_pool:
        return {"msg": "用户没有聊天"}
    user_sessions = msg_pool.get(userid, {})    
    for session_id, history in user_sessions.items():
        # 将历史记录转换为JSON字符串
        history_json = json.dumps(history, ensure_ascii=False)
        print('history_json',history_json)
        GET_ABSTRCT_PROMPT = f"""
        你是一个历史学家，擅长从历史人物的对话中总结讨论主题。
        用户的历史对话是：
        {history}
        请总结讨论主题，不要超过20个字。
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

def process_chat_internal(userid: str, sessionid: str, user_msg: str, story_type: str, func_control: dict) -> str:
    """
    内部聊天处理函数，返回AI回复
    """
    try:
        # 获取msg_pool中user_id和session_id对应的msg列表
        msg_list = msg_pool[userid][sessionid]
        msg_list.append({"role": "user", "content": user_msg})
        
        # 根据关键词查询的信息，渲染为关键词模板
        KW_PARA_PROMPT = ""
        try:
            an_kw = get_user_keywords(msg_list)
            if an_kw.get('is_about_ztaofen'):
                kws = an_kw.get('keywords', [])
                if kws:  # 确保keywords不为空
                    kw_paragraphs_list = get_paras_from_kws(kws)
                    # 循环写入prompt
                    for ky, kw_paragraphs in zip(kws, kw_paragraphs_list):
                        KW_PARA_PROMPT += f"用户的关键词是'{ky}'，\n相关段落是:{kw_paragraphs}\n\n"
        except Exception as e:  
            KW_PARA_PROMPT = ""
            print(f"关键词处理失败: {e}")
        
        # 根据语义去向量数据库查询的信息
        try:
            res = db_util.get_final_nodes_text(summary_index, simple_index, user_query=user_msg)
        except Exception as e:
            res = ""
            print(f"向量数据库查询失败: {e}")
        
        # 制作模板
        GET_AI_ANSWER = f"""
        你要扮演我国历史上的著名人物邹韬奋和用户进行对话。
        你们已经进行了如下对话:
        {msg_list}
        当前的用户发言是：
        {user_msg}
        从用户发言中提取的关键词以及从数据库中抽取的该关键词相关文档是：
        {KW_PARA_PROMPT}
        你还可以参考如下信息：
        {res}
        请给出对用户合适的回应，回复中不需要加入动作或神情描述，只需要给出当事人的语言回复：
        """
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": GET_AI_ANSWER},
            ],
            stream=False
        )
        
        system_msg = response.choices[0].message.content or "抱歉，我无法生成回复。"
        msg_list.append({"role": "system", "content": system_msg})
        msg_pool[userid][sessionid] = msg_list
        
        print(f'语音聊天后的msg_pool: {msg_pool}')
        print(f'语音聊天后的当前用户msg_list: {msg_list}')
        
        return system_msg
        
    except Exception as e:
        print(f"内部聊天处理失败: {e}")
        return "抱歉，我现在无法回复您的消息，请稍后再试。"

@app.post("/upload_audio")
async def upload_audio(
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    session_id: str = Form(...),
    story_type: str = Form(default="x"),
    func_control: dict = Form(default={'Vector': True, 'knowledge': True, 'EsSearch': True, 'Model_enhance': True})
):
    """
    接收前端上传的音频文件，进行语音识别，并返回AI回复
    """
    try:
        # 创建音频存储目录
        audio_dir = "audio_files"
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{user_id}_{session_id}_{timestamp}"
        
        # 保存原始音频文件（webm格式）
        webm_path = os.path.join(audio_dir, f"{filename}.webm")
        
        # 读取并保存文件
        contents = await audio.read()
        with open(webm_path, "wb") as f:
            f.write(contents)
        
        print(f"音频文件已保存: {webm_path}")
        print(f"文件大小: {len(contents)} bytes")
        
        # 可选：转换为MP3格式（需要安装ffmpeg）
        mp3_path = os.path.join(audio_dir, f"{filename}.mp3")
        final_path = webm_path
        final_filename = f"{filename}.webm"
        
        try:
            # 使用ffmpeg转换为MP3（如果系统安装了ffmpeg）
            import subprocess
            result = subprocess.run([
                'ffmpeg', '-i', webm_path, '-acodec', 'libmp3lame', 
                '-ar', '44100', '-ab', '128k', mp3_path, '-y'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # 转换成功，删除原始webm文件
                os.remove(webm_path)
                final_path = mp3_path
                final_filename = f"{filename}.mp3"
                print(f"已转换为MP3格式: {mp3_path}")
        except (ImportError, FileNotFoundError):
            # 没有安装ffmpeg，保留webm文件
            print("未安装ffmpeg，保留WebM格式")
        
        # 进行语音识别
        try:
            recognized_text = recognize_audio_file(final_path)
            
            if not recognized_text:
                recognized_text = "语音识别失败，请重试"
            
            print(f"语音识别结果: {recognized_text}")
            
        except Exception as e:
            print(f"语音识别失败: {str(e)}")
            recognized_text = "语音识别服务暂时不可用"
        
        # 如果识别成功，调用聊天接口获取AI回复
        ai_response = None
        if recognized_text and "失败" not in recognized_text and "不可用" not in recognized_text:
            try:
                # 确保用户和会话在msg_pool中存在
                if user_id not in msg_pool:
                    msg_pool[user_id] = {}
                if session_id not in msg_pool[user_id]:
                    msg_pool[user_id][session_id] = []
                
                # 调用内部聊天处理函数
                ai_response = process_chat_internal(user_id, session_id, recognized_text, story_type)
                
            except Exception as e:
                print(f"AI回复生成失败: {str(e)}")
                ai_response = "AI服务暂时不可用，请稍后重试"
        
        # 为AI回复生成语音
        ai_audio_data = None
        ai_audio_duration = 0
        if ai_response and "失败" not in ai_response and "不可用" not in ai_response:
            try:
                tts_result = synthesize_text(ai_response, voice="longwan")
                if tts_result:
                    ai_audio_data, ai_audio_duration = tts_result
                    print(f"AI回复语音合成成功，时长: {ai_audio_duration}秒")
            except Exception as e:
                print(f"AI回复语音合成失败: {e}")
        
        # 确保ai_response不为None再添加到消息池
        if ai_response is not None:
            msg_pool[user_id][session_id].append({"role": "assistant", "content": ai_response})
        
        return {
            "msg": "语音处理成功",
            "filename": final_filename,
            "path": final_path,
            "size": len(contents),
            "user_id": user_id,
            "session_id": session_id,
            "recognized_text": recognized_text,
            "ai_response": ai_response,
            "ai_audio_data": ai_audio_data,
            "ai_audio_duration": ai_audio_duration
        }
        
    except Exception as e:
        print(f"语音处理失败: {str(e)}")
        return {
            "msg": f"语音处理失败: {str(e)}",
            "filename": None,
            "recognized_text": None,
            "ai_response": None
        }



