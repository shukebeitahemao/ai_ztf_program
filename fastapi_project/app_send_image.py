from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import os
app = FastAPI()
@app.get("/get-image/{image_name}")
async def get_image(image_name: str):
    # 图片存储路径
    image_path = f"static/assets/{image_name}"
    # 检查文件是否存在
    if not os.path.exists(image_path):
        return {"error": "图片不存在"}
    
    # 返回图片文件
    return FileResponse(
        path=image_path,
        filename=image_name,
        media_type="image/png"  # 可以根据实际图片类型调整
    )
