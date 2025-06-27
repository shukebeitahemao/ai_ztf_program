from openai import OpenAI
import sys
import time
def start_ds_client():
    print("正在初始化API客户端...")
    try:
        client = OpenAI(api_key="sk-9263361d03dc4c2dad81f483bf3185df", base_url="https://api.deepseek.com")
        print("API客户端初始化成功")
        return client
    except Exception as e:
        print(f"API客户端初始化失败: {str(e)}", file=sys.stderr)
        sys.exit(1)
if __name__=="__main__":
    # 仅作为模块供外部导入使用，main下方代码用于被python.exe直接执行时，测试模块是否正常
    pass