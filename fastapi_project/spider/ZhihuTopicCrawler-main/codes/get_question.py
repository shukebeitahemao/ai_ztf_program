from playwright.sync_api import sync_playwright
import time

def test_playwright_with_cookie(url, cookie_string):
    """
    使用playwright访问目标页面，携带指定的cookie信息
    
    参数：
        url: 目标页面URL
        cookie_string: cookie字符串
    
    返回：
        bool: 是否成功访问页面
    """
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)  # headless=False 可以看到浏览器界面
        context = browser.new_context()
        
        # 设置cookie
        if cookie_string:
            # 解析cookie字符串并设置
            cookies = []
            for item in cookie_string.split(';'):
                if '=' in item:
                    name, value = item.strip().split('=', 1)
                    cookies.append({
                        'name': name,
                        'value': value,
                        'domain': '.zhihu.com',
                        'path': '/'
                    })
            
            context.add_cookies(cookies)
            print(f"✅ 已设置 {len(cookies)} 个cookie")
        
        # 创建新页面
        page = context.new_page()
        
        try:
            print(f"🌐 正在访问: {url}")
            
            # 访问页面
            response = page.goto(url, wait_until='networkidle', timeout=30000)
            
            if response:
                print(f"✅ 页面访问成功，状态码: {response.status}")
                
                # 获取页面标题
                title = page.title()
                print(f"📄 页面标题: {title}")
                
                # 检查页面内容
                content = page.content()
                if len(content) > 100:
                    print(f"📝 页面内容长度: {len(content)} 字符")
                    print(f"📋 内容预览: {content[:200]}...")
                else:
                    print("⚠️  页面内容可能为空或异常")
                
                return True
            else:
                print("❌ 页面访问失败")
                return False
                
        except Exception as e:
            print(f"❌ 访问页面时出错: {e}")
            return False
            
        finally:
            # 等待几秒让用户看到结果
            time.sleep(3)
            # browser.close()


"""
主函数：测试playwright访问知乎页面
"""
# 测试URL（知乎问题页面）
test_url = "https://www.zhihu.com/question/1919032669615912434"

# 从get_url_text.py中复制的cookie字符串

cookie_string = "_zap=8b12aa03-c82d-4d62-a3b2-0e0a3968d9bf; _xsrf=6c2acedc-3c81-4687-8afc-02c1d978322d; HMACCOUNT_BFESS=A168AA1292E91FB5; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1750406921; HMACCOUNT=A168AA1292E91FB5; d_c0=OLVTcCgsoxqPTsh4EBN1RJMCDg-vCyQXdQw=|1750406919; SESSIONID=tuXdyQ8Gb7O3PGPsjV8JPeyfJN6tbECBqhdEiCkjWyN; JOID=W1gcCk3LRVY4EAduW5FCwu43K8tBtjkOU2ZfXxymexALT083IcxbDFAWB2dUJ2ismXyrcGhtwNqm0fm0gxPzskk=; osd=Ul0VAk_CQF8wEg5rUplAy-s-I8lIszAGUW9aVhSkchUCR00-JMVTDlkTDm9WLm2lkX6idWFlwtOj2PG2ihb6uks=; captcha_session_v2=2|1:0|10:1750406919|18:captcha_session_v2|88:d2tDd3V4emdWRUFraW1OK084UzhuVnhwME5GaGdvMm1qaGpqZSsxRmExL3dMVURJQ3NwNVlxUUQxMThmcm5OUQ==|3aa535c0d9fda2b15ddaed9eca0ace89d3203b32d480b6a2bc0268f164ba82ae; __snaker__id=1ZDj8Ryw9Ir7V09K; gdxidpyhxdE=vzPR7uuhyyqikiUUcSIZHMw%5CoMc6%5CWUL6dUGq1UzOsOIv%5CounVLqXQ%2BNN70QSW6%2FokzHLK%2Bbw7hsbxVzl%2B6qAG9IDE9VbTv%2FlOHImrtJOnjxwnIvLlSOGZ2iUlChZel8Hn9yG4Qx6uMsmogxPmC%2BIUt89Y5AE%2BqLJ56wpoh1bTylSCov%3A1750407822853; DATE=1750406922835; cmci9xde=U2FsdGVkX19S6K3DbcdnTALzfuHnrPRLwKRo6lYKfmAwCbgviLeu9gIv7Wh9WkBSwrCSKEsQDaLGmuvzEc8XLg==; pmck9xge=U2FsdGVkX1/EUII6M/+R0Bd9qkfFZk6QMghojH+D4oQ=; assva6=U2FsdGVkX1+Qt9w3XYfqmMzSyI/ZvwOBhgFrA3Kez1c=; assva5=U2FsdGVkX18uD8MNmJciRmEY2zlgk3anU57VJ6wsXpcwrQQz1m2c/KOM6yUbzCow26Lvs6IDu92HkqVrQvgr4A==; crystal=U2FsdGVkX1+q1nQKYRxMaJ68PwE7vNBfLJbVVAx5vexegsYs0Xy9ekUuTxrTREOtHiW4zmjMmHjuSo13i/jtoF2Ljk7cCym1THExdUzCJClvkm7gPQL2MEFpldj8H8+0IHbjJZyjqcQtrQDQWF7aWd530nmyzKdJN7I9s0Rq915qjpeKMFCF4gQl3KuxNJNASV9FvN5+wKmchN6ev2XsPMLG3P3yvL4/mPAm+uPxThiOp1aSPzpJKihbdXTkDuXX; vmce9xdq=U2FsdGVkX1+TkvWPtvIUjPgB3O2jdM01rJvxmnjJ/mO2RJRKVIrzREem+DCmXvDKQaGNdwZNUJRRpHlI7Ycr7nzJMUq3igYCrDNlbcOxWl+idw6g+O1oXKCqiCEifzpKRHvDPHAtg5oMJesyEixDU2rPuqCZniqJ2OOfr7jASeE=; o_act=login; ref_source=other_https://www.zhihu.com/signin; ui=D52DBE81-92EB-4F9A-B5B7-7F28B8869655; pt_login_sig=7bmVdHiUO6rcGxu0iWc7-T9jrHgxLYLnXlpUich11N2bsfHRb9oRsWr4zpePcmE6; pt_clientip=f6e3240e046c194041e27df888dad5291e1f47f4; pt_serverip=b31f7f0000015cf7; pt_local_token=652410952; uikey=a3fb027fa38b8af3f267af32a7d08589ce0dfe912f2aa258260fe9c48d0dcefd; __aegis_uid=b31f7f0000015cf7-f6e3240e046c194041e27df888dad5291e1f47f4-4546; _qpsvr_localtk=0.5928878490363629; qrsig=dc59f58661297782e6189560e8cd25f45ab9a953b2c021f101d7ea419919711064fe20430d952f375367abae1bb785af00c788f8a085010d47bf8088c8a65166; pt2gguin=o1023339654; ETK=; superuin=o1023339654; supertoken=945692470; superkey=IYjGKPyQ7d2t7an4TlSWsbeBOd8Ap4NDkQHnMMooozI_; pt_recent_uins=e9ba0aca8bcd5319a563ffcdeb76d65c7b3ee64e235bd8241b0d63333f31207a3b56e9c818633b046666dbbbf4dc06324852764359ccdeda; pt_guid_sig=5a28fb12d5b7896741fddf2161268858c788304f709361ac9626dac46b2bcaaf; RK=IE/V/w9aRo; ptnick_1023339654=e4bbbfe4bd9be4b880e5b985e4b880e5b985; ptcz=bcdee45bb1c3a35f81c904b5228d48a8ca92b29a47ab479e678bf9f15005c352; p_uin=o1023339654; pt4_token=fX8xkYktHAQRRJdAYP4vIxVe0Rh8lkanY0sHupRqzpU_; p_skey=a*NpZt1OjDgEDzfr-cJpo-7NmeXe1mOX26Ud9DWuKf8_; pt_oauth_token=4ZDTxSs3ubT4LuXB2328pQtEX1121tiEUirqWqIOw95PS0GMBRyaV6VdVK-WBOrEjpgLacueFGQ_; pt_login_type=3; expire_in=15552000; z_c0=2|1:0|10:1750406937|4:z_c0|92:Mi4xZ2taLUFnQUFBQUE0dFZOd0tDeWpHaGNBQUFCZ0FsVk5HV1ZDYVFBc082bFdBTG9yNTdNYlU5Nm5HcjRjX3RfOWhB|ceec82c65e939806a91fe6523f33df1e74c54014abc1a79b8929b51bf054df37; q_c1=3f23924ea65a41f596f9698298a0405f|1750406938000|1750406938000; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1750406941; BEC=6c53268835aec2199978cd4b4f988f8c; tst=r; BEC=cb95f4cef2a104c988a6ef7edd0de14b; BEC=244e292b1eefcef20c9b81b1d9777823; unlock_ticket=ABBKj-9IVQkXAAAAYAJVTSQeVWh86RJyAHLiyXu_c5e7qwA13pPodw=="

print("🚀 开始测试playwright访问知乎页面")
print("=" * 50)

# 测试访问
success = test_playwright_with_cookie(test_url, cookie_string)

if success:
    print("\n✅ 测试成功！playwright可以正常访问知乎页面")
else:
    print("\n❌ 测试失败！请检查网络连接或cookie是否有效")

print("\n" + "=" * 50)
print("🎯 测试完成")
