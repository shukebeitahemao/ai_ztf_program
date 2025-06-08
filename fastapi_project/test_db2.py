import sqlite3
# def execute_sql_query(sql_query: str):
#     try:
#         # 连接数据库
#         conn = sqlite3.connect('test.db')
#         cursor = conn.cursor()
        
#         # 执行SQL查询
#         cursor.execute(sql_query)
        
#         #获取所有结果
#         results = cursor.fetchall()
        
#         #获取列名
#         column_names = [description[0] for description in cursor.description]
        
#         # 关闭数据库连接
#         conn.close()
        
#         # 打印结果
#         print("查询结果:")
#         print("列名:", column_names)
#         print("数据:", results)
        
#         return {
#             "status": "success",
#             "columns": column_names,
#             "data": results
#         }
        
#     except Exception as e:
#         print(f"查询出错: {str(e)}")
#         return {
#             "status": "error",
#             "message": str(e)
#         }

# # 使用示例
# if __name__ == "__main__":
#     # 示例查询
#     # query = "CREATE TABLE IF NOT EXISTS name (name TEXT,age INTEGER)"
#     query = "SELECT * FROM name"
#     # query = "INSERT OR IGNORE INTO name (name, age) VALUES ('kiwid', 20)"
#     result = execute_sql_query(query)

conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# 执行SQL查询
# cursor.execute("INSERT OR IGNORE INTO name (name, age) VALUES ('kiwid', 20)")
cursor.execute("SELECT * FROM name")

# 先获取列名（在fetchall之前），防止cursor对象被消费
#column_names = [description[0] for description in cursor.description]

# 再获取所有结果
results = cursor.fetchall()

conn.commit()
# 关闭数据库连接
conn.close()

# print("列名:", column_names)
print("查询结果:", results)
