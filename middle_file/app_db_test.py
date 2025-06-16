from fastapi import FastAPI, Request
import sqlite3
from fastapi.responses import JSONResponse

# # 创建数据库连接和表
# def init_db():
#     conn = sqlite3.connect('test.db')
#     cursor = conn.cursor()
    
#     # 创建name表
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS name (
#             name TEXT,
#             age INTEGER
#         )
#     ''')
    
#     # 插入模拟数据
#     sample_data = [
#         ('张三', 25),
#         ('李四', 30),
#         ('王五', 28),
#         ('赵六', 35),
#         ('钱七', 22)
#     ]
    
#     cursor.executemany('INSERT OR IGNORE INTO name (name, age) VALUES (?, ?)', sample_data)
#     conn.commit()
#     conn.close()

# # 初始化数据库
# init_db()
app = FastAPI()
@app.post("/search-by-name")
async def search_by_name(request: Request):
    try:
        # 获取前端传递的name参数
        data = await request.json()
        search_name = data.get('name')
        
        if not search_name:
            return JSONResponse(
                status_code=400,
                content={"error": "请提供name参数"}
            )
        
        # 连接数据库并查询
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, age FROM name WHERE name = ?', (search_name,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                "status": "success",
                "data": {
                    "name": result[0],
                    "age": result[1]
                }
            }
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "未找到匹配的记录"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"服务器错误: {str(e)}"}
        )
