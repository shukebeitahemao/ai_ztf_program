import psycopg2
from psycopg2 import Error

##获取连接对象
def connect_to_postgres():
    try:
        # 连接到PostgreSQL数据库
        connection = psycopg2.connect(
            user="postgres",
            password="wzdshjw123",
            host="localhost",
            port="5432",
            database="first_pg"
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
            column_names = [desc[0] for desc in cursor.description]
            print("列名:", column_names)
            print("查询结果:", results)
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

##将txt_split_file中的文件写入pgsql的article表
def write_to_article():
    import os
    from datetime import datetime

    # 获取txt_split_file目录下所有txt文件
    txt_dir = "chat/txt_split_file"
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
write_to_article()