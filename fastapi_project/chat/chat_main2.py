





#使用llamaindex框架，使用deepseek client和chroma向量数据库，对txt_split_file文件夹下所有文件制作索引



# 创建向量存储
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 读取所有文本文件
documents = SimpleDirectoryReader(
    input_dir="fastapi_project/chat/txt_split_file",
    recursive=True
).load_data()

# 创建索引时直接使用 Settings
index = VectorStoreIndex.from_documents(
    documents,
    vector_store=vector_store
)

#使用文档级摘要索引
from llama_index.core import (
    DocumentSummaryIndex,
    PromptTemplate,
    get_response_synthesizer,
    SimpleDirectoryReader,
)

# 读取原始文档（示例用目录，也可以直接传入已构造的 Document 列表）
docs = SimpleDirectoryReader("txt_split_file/").load_data()
# ✅ 自定义摘要模板 —— {context_str} 会被替换成全文
summary_tmpl = PromptTemplate(
    "请用 3-4 句话总结以下文档，并突出与用户‘{topic}’相关的信息：\n"
    "{context_str}\n"
    "—— 摘要："
)
# LlamaIndex ≥0.10.x 把 summary_template 收进 response_synthesizer
# 也必须在response_synthesizer中查看模板
resp_synth = get_response_synthesizer(
     response_mode="tree_summarize",        # or "tree_summarize"
    summary_template=summary_tmpl
)
# 构建 DocumentSummaryIndex
doc_sum_index = DocumentSummaryIndex.from_documents(
    docs,
    response_synthesizer=resp_synth
)
#查看模板，确认使用了我们指定的模板
# print(resp_synth.get_prompts()["summary_template"].get_template())

#打印索引中每篇文档的摘要
def show_doc_summaries(index: DocumentSummaryIndex):
    """打印索引中每篇文档的摘要"""
    struct = index.index_struct                 # IndexDocumentSummary 对象
    ds = index.docstore

    for doc_id, summary_node_id in struct.doc_id_to_summary_id.items():
        summary_node = ds.get_node(summary_node_id)
        print(f"\n=== 文档 {doc_id} 的摘要 ===")
        print(summary_node.get_text())

show_doc_summaries(doc_sum_index)

#从用户回答获取摘要内容
retriever = doc_sum_index.as_retriever(similarity_top_k=5)

# 用户提问
query = "有哪些文档涉及地方法院？"
# 手动进行检索（结果为 NodeWithScore 对象）
retrieved_nodes = retriever.retrieve(query)
# 输出原文内容
for i, node in enumerate(retrieved_nodes):
    print(f"\n📄 文档片段 #{i+1}（doc_id={node.node.ref_doc_id}）:")
    print(node.node.text[:500], "...")

    

