# -*- coding:utf-8 -*-
from fastapi import FastAPI
from typing import Optional

#以下引入允许模板渲染的包
# 导入pathlib库，用于处理文件路径
import pathlib
# 从fastapi导入Request类，用于处理HTTP请求
from fastapi import Request
# 从fastapi.responses导入HTMLResponse类，用于返回HTML响应
from fastapi.responses import HTMLResponse
# 从fastapi.templating导入Jinja2Templates类，用于模板渲染
from fastapi.templating import Jinja2Templates
# 从fastapi.staticfiles导入StaticFiles类，用于处理静态文件（如CSS、JavaScript、图片等）
from fastapi.staticfiles import StaticFiles

# 创建Jinja2Templates实例，用于模板渲染
# directory参数指定模板文件所在的目录
# pathlib.Path.cwd()获取当前工作目录
# 模板文件将存放在项目根目录下的templates文件夹中
templates = Jinja2Templates(directory=f"{pathlib.Path.cwd()}/templates/")
# 创建StaticFiles实例，用于处理静态文件
# 静态文件（如CSS、JavaScript、图片等）将存放在项目根目录下的static文件夹中
staticfiles = StaticFiles(directory=f"{pathlib.Path.cwd()}/static/")


#错误处理模块：把各种类型的错误包装后返回给前端
from starlette.responses import JSONResponse
async def exception_not_found(request,exc):
    #request,exc按照位置参数而不是名称参数确定，第一个是Request对象，第二个是Exception对象
    return JSONResponse({
        "code":exc.status_code,
        "error":"没有这个请求地址"
    },status_code=exc.status_code)

exception_handlers = {
    404:exception_not_found
}
#也可以处理其它类型的错误以及自定义异常类
# exception_handlers = {
#     ValueError: value_error_handler,
#     KeyError: key_error_handler,
#     ZeroDivisionError: zero_division_handler
# }

app = FastAPI(title="学习FastApi框架文档",
              description="以下是关于fastapi文档的描述",
              version="0.0.1",
              debug=True,
              exception_handlers=exception_handlers)
#使用装饰器来注册路由,tags用于UI展示
@app.get('/app/hello',tags=['hello接口示例'])
def app_hello(name:str):
    #直接给前端返回json数据
    return {'Hello':name}

# 将静态文件目录挂载到FastAPI应用中
# /static 是访问静态文件的URL路径前缀
# staticfiles 是之前定义的StaticFiles实例，用于处理静态文件
# 静态文件处理说明
# staticfiles实例用于处理静态文件（如CSS、JavaScript、图片等）
# 它允许通过URL访问static目录下的文件
# 例如：/static/css/style.css 将访问 static/css/style.css 文件
# 模板渲染说明
# templates实例用于处理HTML模板文件
# 它允许在templates目录下创建模板文件，并通过Jinja2语法进行渲染
# 例如：templates.TemplateResponse("index.html", {"request": request, "data": data})

# name="static" 为这个挂载点指定一个唯一的名称，用于反向引用
# 反向应用说明
# 反向应用是指通过名称来引用已注册的静态文件路径
# 例如：url_for("static", path="css/style.css") 将生成 /static/css/style.css
# 这在模板中特别有用，可以动态生成静态文件的URL
# 使用反向应用可以避免硬编码URL路径，使代码更加灵活和可维护
# 当静态文件路径发生变化时，只需要修改mount时的路径，而不需要修改所有引用该路径的地方
app.mount("/static",staticfiles,name="static")

#也可以用装饰器修饰async def的异步函数
@app.get('/',response_class=HTMLResponse)
# 定义一个异步函数get_response，接收一个Request类型的参数request
# Request参数包含了HTTP请求的所有信息，如请求头、查询参数等
async def get_response(request:Request):
    # 使用templates.TemplateResponse渲染index.html模板
    # 第一个参数"index.html"指定要渲染的模板文件
    # 第二个参数是一个字典，包含要传递给模板的变量
    # 'request'键对应的值会被传递给模板，使模板能够访问请求信息，index.html中没有直接使用request变量
    # 但是可以使用request.some_attribute的形式使用
    # 这是FastAPI的模板渲染机制，使用Jinja2模板引擎
    return templates.TemplateResponse("index.html",{'request':request})


#完整的启动命令
#0.0.0.0指的是允许来自任意IP地址的主机访问，8888是自定义的访问接口
# uvicorn main:app --reload --host 0.0.0.0 --port 8888
# ctrl+c或者任务管理器终止服务

#函数方法启动
#if __name__ =="__main__":
# import uvicorn
# uvicorn.run(app='main:app',port,reload,host)

from fastapi.responses import PlainTextResponse
#开启debug模式，在前端网页上看到后端的报错信息
@app.get('/app/debug')
def index():
    1900/0
    #这个return完全没有用的
    return PlainTextResponse('一个错误')


