from playwright.sync_api import sync_playwright
import time

def get_zhihu_cookies():
    """
    使用playwright从知乎网站获取cookie信息，包含登录步骤
    返回格式化的cookie字符串
    """
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)  # headless=False 可以看到浏览器操作过程
        page = browser.new_page()
        
        try:
            # 访问知乎首页
            print("🌐 正在访问知乎网站...")
            page.goto("https://www.zhihu.com")
            
            # 等待页面加载
            time.sleep(3)
            
            # 检查是否需要登录
            login_button = page.locator("text=登录").first
            if login_button.is_visible():
                print("🔐 检测到需要登录，开始登录流程...")
                
                # 点击登录按钮
                login_button.click()
                time.sleep(2)
                
                # 等待用户手动登录
                print("⏳ 请在浏览器中手动完成登录操作...")
                print("💡 登录完成后，程序将自动获取cookie信息")
                
                # 等待登录完成（检测登录状态变化）
                page.wait_for_url("https://www.zhihu.com/", timeout=100000)  # 100秒超时
                
                print("✅ 登录完成！")
                time.sleep(2)
            
            # 获取所有cookie
            cookies = page.context.cookies()
            
            # 格式化cookie字符串
            cookie_string = ""
            for cookie in cookies:
                if cookie_string:
                    cookie_string += "; "
                cookie_string += f"{cookie.get('name', '')}={cookie.get('value', '')}"
            
            print("🍪 成功获取cookie信息:")
            print(cookie_string)
            
            return cookie_string
            
        except Exception as e:
            print(f"❌ 获取cookie时出错: {e}")
            return ""
            
        finally:
            browser.close()

if __name__ == "__main__":
    get_zhihu_cookies()

