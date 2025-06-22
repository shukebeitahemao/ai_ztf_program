from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DEEPSEEK_API: str 
    USERS: str 
    PASSWORD: str 
    DATABASE: str 
    ARTICLE_DIR: str
    ALIBABA_CLOUD_ACCESS_KEY_ID: str
    ALIBABA_CLOUD_ACCESS_KEY_SECRET: str
    DASHSCOPE_API_KEY: str
    DASHSCOPE_BASE_URL: str
    
    class Config:
        #注意：这里需要指定env文件的路径，否则会报错，从fastapi主项目入口开始写
        env_file = "fastapi_project/.env"
        env_file_encoding = "utf-8"

settings = Settings()
