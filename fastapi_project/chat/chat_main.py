import chat_util
from chat_util import start_llama_query
from pathlib import Path
from llama_index.core import StorageContext, load_index_from_storage
import fastapi
#初始化llamaindex的相关配置
chat_util.initialize_llamaindex(deepseekapi="sk-32361150eb3b467eb085d49308f6906d")
# 加载VectorStoreIndex
storage_context = StorageContext.from_defaults(persist_dir="fastapi_project/chat/chat/index_store/simpleindex")
loaded_simpleindex = load_index_from_storage(storage_context)
# 加载DocumentSummaryIndex
storage_context = StorageContext.from_defaults(persist_dir="fastapi_project/chat/chat/index_store/doc_sum_index")
loaded_doc_sum_index = load_index_from_storage(storage_context)
# res = chat_util.get_docs_from_simpleindex(loaded_simpleindex, user_question='地方法院是什么？')
# print(f"测试结果: {res[:100]}...")
chat_prompt = f"""

"""

