import psycopg2
from psycopg2 import Error

def connect_to_postgres():
    try:
        # 连接到PostgreSQL数据库
        connection = psycopg2.connect(
            user="postgres",
            password="root",
            host="localhost",
            port="5432",
            database="first_pg"
        )
        return connection
    except Error as e:
        print(f"连接数据库时出错: {e}")
        return None

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

# 使用示例
if __name__ == "__main__":
    # SELECT查询示例
    select_query = "SELECT * FROM activity"
    execute_query(select_query)
    
    # # INSERT示例
    # insert_query = "INSERT INTO your_table (column1, column2) VALUES (%s, %s)"
    # insert_params = ('value1', 'value2')
    # execute_query(insert_query, insert_params)
    
    # # UPDATE示例
    # update_query = "UPDATE your_table SET column1 = %s WHERE column2 = %s"
    # update_params = ('new_value', 'value2')
    # execute_query(update_query, update_params)
    
    # # DELETE示例
    # delete_query = "DELETE FROM your_table WHERE column1 = %s"
    # delete_params = ('value1',)
    # execute_query(delete_query, delete_params)
