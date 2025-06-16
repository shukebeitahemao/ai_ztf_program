from .db_util import execute_query,write_to_article
import uuid
import json
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
            # 清理标题中的特殊字符
            title = title.strip().replace('/', '_').replace('\\', '_')
            
            # 写入txt文件
            output_file = os.path.join(output_dir, f"{title}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content.strip())
                
    print(f"文件已分割完成，保存在: {output_dir}")





#执行    & D:/python_envs/ai_project/Scripts/python.exe -m fastapi_project.util.db_util



# # 生成3个不同的user_id
# user_ids = [str(uuid.uuid4()) for _ in range(3)]

# # 为每个user_id生成3个不同的session_id并创建对应的历史记录
# for user_id in user_ids:
#     # 为每个用户生成3个session_id
#     session_ids = ['session_'+str(uuid.uuid4()) for _ in range(3)]
    
#     # 为每个session创建历史记录
#     for session_id in session_ids:
#         chat_history = [
#             {"role": "assistant", "content": "你好"},
#             {"role": "user", "content": "邹韬奋是谁？"},
#             {"role": "assistant", "content": "他是一个伟大的作家"},
#             {"role": "user", "content": "你吃了么"},
#         ]
        
#         # 将历史记录转换为JSON字符串
#         history_json = json.dumps(chat_history, ensure_ascii=False)
        
#         # 插入数据库
#         insert_query = f"""
#         INSERT INTO message (user_id, session_id, history)
#         VALUES ('{user_id}', '{session_id}', '{history_json}');
#         """
#         execute_query(insert_query)

# print("已成功创建3个用户，每个用户3个会话")

# 为message表添加abstract列
# alter_query = """
# ALTER TABLE message 
# ADD COLUMN abstract TEXT DEFAULT '这是摘要';
# """
# execute_query(alter_query)
# print("已成功为message表添加abstract列")

# select_query = """
# SELECT session_id,update_time,abstract FROM message limit 2;
# """
# results = execute_query(select_query)
# print(type(results))



