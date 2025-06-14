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
def initialize_llamaindex(deepseekapi,chroma_collection_name="txt_documents"):
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

    # 初始化 Chroma 客户端
    chroma_client = chromadb.Client()
    chroma_collection = chroma_client.create_collection(chroma_collection_name)
    # 创建向量存储
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    return llm,embed_model,chroma_collection,vector_store

##从文档中创建简单索引
def generate_index(vector_store,input_dir="txt_split_file"):
    # 读取所有文本文件
    documents = SimpleDirectoryReader(
        input_dir=input_dir,
        recursive=True
    ).load_data()

    # 创建索引时直接使用 Settings
    simpleindex = VectorStoreIndex.from_documents(
        documents,
        vector_store=vector_store
    )
    return documents,simpleindex

## 从简单索引中,根据用户问题，获取相关文档,拼接为一个字符串输出
def get_docs_from_simpleindex(simpleindex,user_question):
    # 创建检索器，检索器只能检索信息，不需要进一步创建搜索或对话引擎
    retriever = simpleindex.as_retriever(similarity_top_k=3)
    # 获取相关文档
    retrieved_docs = retriever.retrieve(user_question)
    result = ''
    # 打印检索到的文档
    for doc in retrieved_docs:
        result += doc.text + '\n'
    return result

##创建摘要索引，自定义摘要内容
def generate_summary_index(douments):
    
    summary_tmpl = PromptTemplate(
    "请用1-2句话总结以下文档，并提出1-2个该文档能回答的用户问题：\n"
    "{context_str}\n"
    "—— 摘要：")
    # LlamaIndex ≥0.10.x 把 summary_template 收进 response_synthesizer
    resp_synth = get_response_synthesizer(
        response_mode="tree_summarize",        # or "tree_summarize"
        summary_template=summary_tmpl
    )
    # 构建 DocumentSummaryIndex
    doc_sum_index = DocumentSummaryIndex.from_documents(
        # # 读取原始文档（示例用目录，也可以直接传入已构造的 Document 列表）
        # docs = SimpleDirectoryReader("txt_split_file/").load_data()
        douments,
        response_synthesizer=resp_synth
    )
    return doc_sum_index

##打印每篇文档对应的摘要
def show_doc_summaries(index: DocumentSummaryIndex):
    """打印索引中每篇文档的摘要"""
    struct = index.index_struct                 # IndexDocumentSummary 对象
    ds = index.docstore

    for doc_id, summary_node_id in struct.doc_id_to_summary_id.items():
        summary_node = ds.get_node(summary_node_id)
        print(f"\n=== 文档 {doc_id} 的摘要 ===")
        print(summary_node.get_text())

##根据用户提问，使用摘要索引获得相关文档
def get_docs_from_summaryindex(doc_sum_index,query):
    retriever = doc_sum_index.as_retriever(similarity_top_k=3)
    # 手动进行检索（结果为 NodeWithScore 对象）
    retrieved_nodes = retriever.retrieve(query)
    result = ''
    # 输出原文内容
    for i, node in enumerate(retrieved_nodes):
        result += node.node.text + '\n'
    return result

def start_llama_query(deepseekapi):
    #split_txt_files()
    llm,embed_model,chroma_collection,vector_store=initialize_llamaindex(deepseekapi=deepseekapi)
    documents,simpleindex = generate_index(vector_store=vector_store)
    doc_sum_index = generate_summary_index(documents)
    return simpleindex,doc_sum_index












