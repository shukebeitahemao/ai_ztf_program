import psycopg2
from psycopg2 import Error
import re 
import os
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, DocumentSummaryIndex
from llama_index.core import PromptTemplate, get_response_synthesizer, load_index_from_storage
from llama_index.core import Document, StorageContext
from llama_index.core.settings import Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.deepseek import DeepSeek
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.response_synthesizers import ResponseMode
from fastapi_project.util.chat_util import initialize_llamaindex
from fastapi_project.settings import settings

##获取连接对象
def connect_to_postgres():
    try:
        # 连接到PostgreSQL数据库
        connection = psycopg2.connect(
            user=settings.USERS,
            password=settings.PASSWORD,
            host="localhost",
            port="5432",
            database=settings.DATABASE
        )
        return connection
    except Error as e:
        print(f"连接数据库时出错: {e}")
        return None

#执行查询
def execute_query(query, params=None):
    try:
        connection = connect_to_postgres()
        if connection is None:
            return
        
        cursor = connection.cursor()
        
        # 执行查询
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        # 如果是SELECT查询，获取结果
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            # 获取列名
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []
            # print("列名:", column_names)
            # print("查询结果:", results)
            return results
        else:
            # 对于INSERT、UPDATE、DELETE操作，获取受影响的行数
            affected_rows = cursor.rowcount
            print(f"操作影响的行数: {affected_rows}")
            
        # 提交事务
        connection.commit()
        
    except Error as e:
        print(f"执行查询时出错: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("数据库连接已关闭")

#创建article表
def create_article_table():
    query = """
    CREATE TABLE IF NOT EXISTS article (
        id SERIAL,
        title TEXT,
        body TEXT,
        tags text[],
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_query(query)
    return None

#创建message表
def create_message_table():
    query = """
DROP TABLE IF EXISTS message;
CREATE TABLE IF NOT EXISTS message (
    user_id TEXT,
    session_id TEXT,
    history TEXT,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    abstract TEXT DEFAULT '这是摘要'
);"""
    execute_query(query)
    return None

#创建baidu_news表


##将指定文件夹中的文件写入pgsql的article表
def write_to_article(txt_dir):
    import os
    from datetime import datetime

    # 获取txt_split_file目录下所有txt文件
    txt_files = [f for f in os.listdir(txt_dir) if f.endswith('.txt')]

    for txt_file in txt_files:
        # 构建完整的文件路径
        file_path = os.path.join(txt_dir, txt_file)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 准备SQL插入语句
        insert_query = """
        INSERT INTO article (title, body, tags, updated_at)
        VALUES (%s, %s, %s, %s)
        """
        
        # 准备参数
        params = (
            txt_file,  # title
            content,   # body
            [],        # tags (空数组)
            datetime.now()  # updated_at
        )
        
        # 执行插入
        execute_query(insert_query, params)
    return None

##随机生成三条message信息到postgresql数据库的message表
import uuid
import json
def generate_message_info():
    # 生成3个不同的user_id
    user_ids = [str(uuid.uuid4()) for _ in range(3)]
    # 为每个user_id生成3个不同的session_id并创建对应的历史记录
    for user_id in user_ids:
        # 为每个用户生成3个session_id
        session_ids = ['session_'+str(uuid.uuid4()) for _ in range(3)]
        # 为每个session创建历史记录
        for session_id in session_ids:
            chat_history = [
                {"role": "assistant", "content": "你好"},
                {"role": "user", "content": "邹韬奋是谁？"},
                {"role": "assistant", "content": "他是一个伟大的作家"},
                {"role": "user", "content": "你吃了么"},
            ]
            
            # 将历史记录转换为JSON字符串
            history_json = json.dumps(chat_history, ensure_ascii=False)
            
            # 插入数据库
            insert_query = f"""
            INSERT INTO message (user_id, session_id, history)
            VALUES ('{user_id}', '{session_id}', '{history_json}');
            """
            execute_query(insert_query)
    return None




## 从原始文档中生成两级索引，一层是summaryIndex
##创建摘要索引，自定义摘要内容
def generate_summary_index(documents,prompt="""请用1-2句话总结以下文档，并提出1-2个该文档能回答的用户问题：\n
    {context_str}\n
    "—— 摘要："""):
    #初始化 Chroma 客户端
    chroma_client = chromadb.Client()
    chroma_collection = chroma_client.get_or_create_collection("text_doc1")
    # 创建向量存储orm
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    summary_tmpl = PromptTemplate(prompt)
    # LlamaIndex ≥0.10.x 把 summary_template 收进 response_synthesizer
    resp_synth = get_response_synthesizer(
        response_mode=ResponseMode.TREE_SUMMARIZE,
        summary_template=summary_tmpl
    )
    # 构建 DocumentSummaryIndex
    
    doc_sum_index = DocumentSummaryIndex.from_documents(
        documents,
        response_synthesizer=resp_synth,
        vector_store=vector_store
    )
    return doc_sum_index


def generate_simple_index(documents):
    # 按换行符分割，并禁用自动句子分割
    splitter = SentenceSplitter(
        separator="\n\n",  # 强制按换行符切分
        chunk_size=500,  # 可选：防止单个node过长
        chunk_overlap=0,  # 无重叠
        paragraph_separator="\n\n",  # 明确段落分隔符
        secondary_chunking_regex="\n\n",  # 二级分割同样用换行符
    )

    # 分割并保留doc_id
    nodes = []
    for doc in documents:
        # 对当前doc生成nodes
        doc_nodes = splitter.get_nodes_from_documents([doc])
        # 为每个node添加原doc_id到metadata
        for node in doc_nodes:
            node.metadata["doc_id"] = doc.doc_id
        nodes.extend(doc_nodes)

    # 验证输出
    for node in nodes:
        print(f"Node ID: {node.node_id}, Doc ID: {node.metadata['doc_id']}, Text: {node.text[:20]}...")

    # 创建索引（新版无需ServiceContext）
    index = VectorStoreIndex(nodes)
    return index

##根据用户提问，使用摘要索引获得相关文档
def get_docs_from_summaryindex(doc_sum_index, query, k=3):
    retriever = doc_sum_index.as_retriever(similarity_top_k=k)
    retrieved_nodes = retriever.retrieve(query)
    
    print(f"检索到 {len(retrieved_nodes)} 个节点")
    
    seen_doc_ids = set()
    result = []
    
    for node in retrieved_nodes:
        ref_doc_id = node.node.ref_doc_id
        if ref_doc_id not in seen_doc_ids:
            seen_doc_ids.add(ref_doc_id)
            
            # 使用正确的方法获取摘要
            try:
                summary = doc_sum_index.get_document_summary(ref_doc_id)
                # print(f"成功获取文档 {ref_doc_id} 的摘要: {summary[:100]}...")
            except Exception as e:
                print(f"获取文档 {ref_doc_id} 摘要时出错: {e}")
                # 如果无法获取摘要，使用文本的前200个字符作为替代
                summary = node.node.text[:200] + "..." if len(node.node.text) > 200 else node.node.text
            
            result.append({
                'ref_doc_id': ref_doc_id,
                'score': node.score if node.score is not None else 0.0,
                'text': node.node.text,
                'summary': summary
            })
    
    return result

##仅仅创建两个index
def create_summary_and_simple_index():
    # 初始化LLM和嵌入模型
    llm, embed_model = initialize_llamaindex(
        deepseekapi=settings.DEEPSEEK_API  # 替换为您的DeepSeek API密钥
    )
    documents = SimpleDirectoryReader(input_dir=os.path.join("fastapi_project", "data")).load_data()
    for doc in documents:
        # 将原始doc_id存储在metadata中
        doc.metadata['original_doc_id'] = doc.doc_id
    doc_sum_index = generate_summary_index(documents)
    index = generate_simple_index(documents)
    return index,doc_sum_index

##保存两个index
def save_indexes(index,doc_sum_index):
    index.storage_context.persist(os.path.join("fastapi_project", "store", "simpleindex"))
    doc_sum_index.storage_context.persist(os.path.join("fastapi_project", "store", "summaryindex"))

##保存两个index
def save_news_indexes(doc_sum_index):
    doc_sum_index.storage_context.persist("fastapi_project\\store\\news_summaryindex")

##加载两个index
def load_indexes():
    llm, embed_model = initialize_llamaindex(deepseekapi=settings.DEEPSEEK_API)
    # 加载VectorStoreIndex
    storage_context = StorageContext.from_defaults(persist_dir=os.path.join("fastapi_project", "store", "simpleindex"))
    loaded_simpleindex = load_index_from_storage(storage_context)

    # 加载DocumentSummaryIndex
    storage_context = StorageContext.from_defaults(persist_dir=os.path.join("fastapi_project", "store", "summaryindex"))
    loaded_doc_sum_index = load_index_from_storage(storage_context)
    return loaded_simpleindex,loaded_doc_sum_index

# 创建检索器，检索器只能检索信息，不需要进一步创建搜索或对话引擎
def get_final_nodes_text(loaded_simpleindex,loaded_doc_sum_index,user_query):
    res = get_docs_from_summaryindex(loaded_doc_sum_index,query=user_query)
    selected_doc_ids = [r['ref_doc_id'] for r in res]
    retriever = loaded_simpleindex.as_retriever(similarity_top_k=5)
    retrieved_docs = retriever.retrieve(user_query)
    res_text = ''
    for nodeWithScore in retrieved_docs:
        if nodeWithScore.node.metadata['original_doc_id'] in selected_doc_ids:
            res_text += nodeWithScore.node.text + '\n\n'
    return res_text

if __name__=="__main__":
    # print(settings.DEEPSEEK_API)
    # print(".env文件信息成功加载！")
    # index,doc_sum_index=create_summary_and_simple_index()
    # save_indexes(index,doc_sum_index)
    # print("两个索引创建成功")
    # loaded_simpleindex,loaded_doc_sum_index=load_indexes()
    # print("两个索引加载成功")
    # res_text=get_final_nodes_text(loaded_simpleindex,loaded_doc_sum_index,user_query="章先生是谁？")
    # print(res_text)
    # connect_to_postgres()
    # print("数据库连接成功！")
    # create_article_table()
    # print("article表创建成功")
    # create_message_table()
    # print("message表创建成功")
    # generate_message_info()
    # print("message表随机生成三条信息成功")
    # write_to_article(settings.ARTICLE_DIR)
    # print("txt_files文件夹中的txt文件写入pgsql的article表成功!")
    # load_indexes()
    # print("两个索引加载成功")
    query = """
    select * from(
select distinct on(content_length)* from(
SELECT * FROM baidu_news 
WHERE DATE_TRUNC('minute', created_at) = (
    SELECT MAX(DATE_TRUNC('minute', created_at)) FROM baidu_news
) and content_length > 100) as result) as b
order by  hottopic;
    """
    res = execute_query(query)
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
    df_news['comments'] = system_msg_list
    df_news.to_csv('comments.csv')
        



    



