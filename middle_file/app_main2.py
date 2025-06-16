from fastapi import FastAPI
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
app = FastAPI(exception_handlers=exception_handlers)