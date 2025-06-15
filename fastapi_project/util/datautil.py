from .db_util import execute_query,write_to_article
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


##从指定文件夹中将数据加载到postgresql数据库

#将D:\ai_ztf_resouce\txt_files文件夹中所有txt文件写入pgsql的article表
write_to_article("D:\\ai_ztf_resouce\\txt_files")
#执行    & D:/python_envs/ai_project/Scripts/python.exe -m fastapi_project.util.db_util
