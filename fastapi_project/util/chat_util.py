import re 
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader,DocumentSummaryIndex
from llama_index.core import PromptTemplate,get_response_synthesizer
from llama_index.core.settings import Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.deepseek import DeepSeek
import chromadb
import os
#====================================
#测试：读取txt_file文件夹下指定txt文档并打印
def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"文件内容：\n{content}")
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误：{str(e)}")

# 测试读取指定文件
# test_file = "txt_file/地方法院.txt"
# read_txt_file(test_file)

#对txt_file文件下每个txt文件，按照\n进行分割，输出为单个txt文件到txt_spilt_file文件夹下
#使用with open(file_path, 'r', encoding='utf-8') as f:
            # content = f.read()
            # print(repr(content))
#查看文档使用的分割符号，注意windows使用\r\n而不是\n\n作为段落分隔符

#对指定文件夹下的所有txt文档，按照\n进行切割后形成多个txt文档，保存到output_file文件夹下
def split_txt_files(source_file='fastapi_project//chat//txt_file', output_file='fastapi_project//chat//txt_split_file'):
    # 创建输出目录
    if not os.path.exists(output_file):
        os.makedirs(output_file)
    
    # 遍历txt_file目录下的所有文件
    for filename in os.listdir(source_file):
        if filename.endswith('.txt'):
            input_path = os.path.join(source_file, filename)
            
            # 读取文件内容
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 统一换行符，将\r\n和\r都转换为\n
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            
            # 按空行分割内容（一个或多个换行符）
            sections = re.split(r'\n', content)
            
            # 为每个分割后的部分创建新文件
            for i, section in enumerate(sections):
                if section.strip():  # 跳过空段落
                    output_filename = f"{os.path.splitext(filename)[0]}_{i+1}.txt"
                    output_path = os.path.join(output_file, output_filename)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(section.strip())
#split_txt_files()

#初始化llamaindex相关配置,.默认使用deepseek
def initialize_llamaindex(deepseekapi):
    # 初始化 DeepSeek 客户端
    llm = DeepSeek(
        api_key=deepseekapi,  # 替换为你的 DeepSeek API key
        model="deepseek-chat"
    )
    # 初始化 HuggingFace 嵌入模型
    embed_model = HuggingFaceEmbedding(
        #这是北京智源人工智能研究院（BAAI）开发的开源模型
        model_name="BAAI/bge-large-zh-v1.5"
    )

    # 替换 ServiceContext 创建
    Settings.llm = llm
    Settings.embed_model = embed_model

    # # 初始化 Chroma 客户端
    # chroma_client = chromadb.Client()
    # #新建或者连接已有的choroma
    # chroma_collection = chroma_client.get_or_create_collection(chroma_collection_name)
    # # 创建向量存储
    # vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    return llm,embed_model

def show_doc_summaries(index: DocumentSummaryIndex):
    """打印索引中每篇文档的摘要"""
    struct = index.index_struct
    ds = index.docstore
    
    # 在新版本中，正确的遍历方式是访问 struct 的 doc_summary_mapping 属性
    if hasattr(struct, 'doc_summary_mapping'):
        for doc_id, summary_id in struct.doc_summary_mapping.items():
            summary_node = ds.get_node(summary_id)
            # BaseNode 使用 get_content() 获取文本
            summary_text = summary_node.get_content()
            print(f"\n=== 文档 {doc_id} 的摘要 ===")
            print(summary_text)
    else:
        # 兼容旧版本的备用方案
        for doc_id, summary_id in struct.items():
            summary_node = ds.get_node(summary_id)
            summary_text = summary_node.get_content()
            print(f"\n=== 文档 {doc_id} 的摘要 ===")
            print(summary_text)

def find_paragraphs_with_keyword(content, keyword: str,n=5) -> list:
    """
    在文本文件中查找包含关键词的段落
    
    Args:
        file_path: 文本文件路径
        keyword: 要查找的关键词
        
    Returns:
        包含关键词的段落列表
    """
    try:
        # with open(file_path, 'r', encoding='utf-8') as f:
        #     content = f.read()
            
        # 按\n\n分割成段落
        paragraphs = content.split('\n\n')
        
        # 过滤出包含关键词的段落
        matching_paragraphs = [p.strip() for p in paragraphs if keyword in p]
        
        return matching_paragraphs[:n] #返回前5个段落
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return []

def get_user_keywords(chat_history):
    from llama_index.llms.deepseek import DeepSeek
    import json
    llm = DeepSeek(
            api_key="sk-1ce00a653d2c46238249e685eb3a9c7d",  # 替换为你的 DeepSeek API key
            model="deepseek-chat"
        )
        # 使用llm进行查询

    # chat_history=[
    #         {"role": "assistant", "content": "你好"},
    #         {"role": "user", "content": "邹韬奋是谁？"},
    #         {"role": "assistant", "content": "他是一个伟大的作家"},
    #         {"role": "user", "content": "你吃了么"},
    #     ]
    GET_USER_KEYWORDS="""
    以下是AI和用户的部分聊天记录，用户可能在和AI（assistant）讨论邹韬奋的有关信息，也有可能并不是和AI讨论邹韬奋的有关信息。
    请根据聊天记录判断，聊天记录中最后一句用户发言是否围绕邹韬奋在讨论，输出布尔字段：ture或者false。
    如果是，则进一步提取用户发言中的关键词，输出关键词列表。关键词将用于在一个邹韬奋作品数据库中进行搜索。
    你应该尽量提取能体现邹韬奋信息的特殊名词和动词，避免提取一般性的词汇。
    答案以json格式输出，json格式为：{"is_about_ztaofen":true,"keywords":["关键词1","关键词2","关键词3"]}
    聊天记录是：\n\n
    {chat_history}
    """
    GET_USER_KEYWORDS = GET_USER_KEYWORDS.replace("{chat_history}",str(chat_history))
    try:
        response = llm.complete(GET_USER_KEYWORDS)
        json_str = response.text.strip('```json\n').strip('```')
        json_data = json.loads(json_str)
        return json_data
    except Exception as e:
        return {"is_about_ztaofen":False,"keywords":[]}

# 使用 requests 库发送 GET 请求到 Elasticsearch,获取k个文档
def get_es_docs(kw,k=5):
    import requests,json
    # 构建查询 URL
    url = "http://localhost:9200/article/_search"
    params = {
        "q": "body:{kw}".format(kw=kw),
        "size": "{k}".format(k=k),
        "pretty": "true"
    }
    # 发送 GET 请求
    response = requests.get(url, params=params)
    # print('params',params)
    body_list = []
    res_list = json.loads(response.text)['hits']['hits']
    for res in res_list:
        body_list.append(res['_source']['body'])
    return body_list

def get_paras_from_kws(kws):
    kw_paragraphs_list = []  # 期望得到: [ [邹韬奋的段落], [生活的段落] ]   
    for kw in kws:
        docs = get_es_docs(kw)
        
        # 这是为当前关键词找到的所有段落
        paragraphs_for_this_kw = [] 
        
        for doc in docs:
            paragraphs = find_paragraphs_with_keyword(doc, kw,n=5)
            #不是append，因此不会产生嵌套列表
            paragraphs_for_this_kw.extend(paragraphs)
            
        # 修正：将当前关键词的段落列表添加到最终结果中
        kw_paragraphs_list.append(paragraphs_for_this_kw)
    return kw_paragraphs_list
















