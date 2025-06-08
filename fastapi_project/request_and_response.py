#此处讲解request和response对象
#使用fastapi写一个解析前端post数据，进行处理，并返回json响应的示例函数
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 定义请求数据模型，进行数据校验
class UserData(BaseModel):
    name: str
    age: int
    email: Optional[str] = None  #允许前端可选传或者不传
    class Config:
        extra = "forbid"  # 禁止额外参数，有额外参数返回422错误
        #extra = "allow"  # 允许额外参数,通过 user_data.__dict__ 访问
        #extra = "ignore"  # 默认行为，忽略额外参数，不报错，但是__dict__里面也不保留

@app.post("/process-user")
async def process_user_data(user_data: UserData):
    # 处理接收到的数据
    processed_data = {
        "message": f"成功处理用户 {user_data.name} 的数据",
        "user_info": {
            "name": user_data.name,
            "age": user_data.age,
            "email": user_data.email
        },
        "status": "success"
    }
    
    return processed_data

# 使用Request对象直接处理原始请求数据
@app.post("/raw-data")
async def process_raw_data(request: Request):
    # 获取原始JSON数据
    #request.json()是一个异步函数，在调用它的时候必须使用awit关键字，等待其执行结果
    raw_data = await request.json()
    
    # 处理数据
    result = {
        "received_data": raw_data,
        "message": "成功接收原始数据",
        "status": "success"
    }
    
    return result

