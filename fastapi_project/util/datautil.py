from .db_util import (execute_query,
                      write_to_article,
                      generate_summary_index,
                      get_docs_from_summaryindex,
                      save_news_indexes)
from .chat_util import initialize_llamaindex
from ..settings import settings
from llama_index.core.settings import Settings
from llama_index.llms.deepseek import DeepSeek
import uuid
import json
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, DocumentSummaryIndex
#为什么这里写.db_util，而不是from db_util import execute_query,write_to_article
def split_markdown_by_heading(markdown_file: str, output_dir: str):
    """
    将markdown文件按一级标题分割成多个txt文件
    
    Args:
        markdown_file: markdown文件路径
        output_dir: 输出目录路径
    """
    import os
    from pathlib import Path
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取markdown文件
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按一级标题分割
    sections = content.split('# ')
    
    # 跳过第一个空部分
    for section in sections[1:]:
        # 获取标题和内容
        lines = section.split('\n', 1)
        if len(lines) == 2:
            title, content = lines
            # 清理标题中的Windows文件名不允许的特殊字符
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
            title = title.strip()
            for char in invalid_chars:
                title = title.replace(char, '_')
            # 移除开头和结尾的点，因为Windows不允许
            title = title.strip('.')
            # 如果标题为空，使用默认名称
            if not title:
                title = f"section_{len(sections)}"
            # 判断文本长度，如果大于300才写入
            if len(content.strip()) > 300:
                # 写入txt文件
                output_file = os.path.join(output_dir, f"{title}.txt")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content.strip())
                
    print(f"文件已分割完成，保存在: {output_dir}")

if __name__ == "__main__":
    llm, embed_model = initialize_llamaindex(deepseekapi=settings.DEEPSEEK_API)
    #从md转txt文件
    # split_markdown_by_heading("D:\\ai_ztf_resouce\\reading_material\\新闻作品.md","D:\\ai_ztf_resouce\\news_txt_files")
    # print("文件已分割完成，保存在: D:\\ai_ztf_resouce\\news_txt_files")
    #加载txt文件为documents
    documents = SimpleDirectoryReader(input_dir="D:\\ai_ztf_resouce\\news_txt_files\\").load_data()
    #生成summary_index
    prompt = """根据以下文档提取5个主题关键词，示例："民生，税务，政府，养老金，上调税率"，文档是：\n
    {context_str}\n
    "—— 关键词："""
    summary_index = generate_summary_index(documents,prompt)
    #保存summary_index
    summary_index.storage_context.persist(persist_dir="fastapi_project\\store\\news_summaryindex")
    print("summary_index已保存")
