from .db_util import execute_query,write_to_article
from ..settings import settings
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import psycopg2
from psycopg2 import Error
# 结合 Selenium 和 Trafilatura 的完整解决方案
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI

def selenium_trafilatura_extract(url, driver=None, wait_time=3, save_html=False):
    """
    使用 Selenium 获取网页 HTML，然后用 Trafilatura 提取中文内容
    
    Args:
        url (str): 目标网页URL
        driver: Selenium WebDriver对象，如果为None会创建新的
        wait_time (int): 页面加载等待时间（秒）
        save_html (bool): 是否保存HTML文件到本地
    
    Returns:
        dict: 包含提取内容和元数据的字典
    """
    
    # 检查是否安装了trafilatura
    try:
        import trafilatura
    except ImportError:
        return {
            'success': False,
            'error': 'trafilatura未安装，请运行: pip install trafilatura',
            'url': url
        }
    
    # 创建或使用现有的driver
    driver_created = False
    if driver is None:
        try:
            from selenium import webdriver
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # 无头模式，提高效率
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            driver = webdriver.Chrome(options=options)
            driver_created = True
            print(f"✅ 创建了新的Chrome Driver")
        except Exception as e:
            return {
                'success': False,
                'error': f'无法创建WebDriver: {str(e)}',
                'url': url
            }
    
    try:
        print(f"🌐 正在访问: {url}")
        
        # 访问网页
        driver.get(url)
        
        # 等待页面加载
        time.sleep(wait_time)
        
        # 等待body元素加载完成
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except:
            print("⚠️ 页面加载可能不完整，继续处理...")
        
        # 获取页面标题
        page_title = driver.title
        print(f"📄 页面标题: {page_title}")
        
        # 获取完整的HTML源码
        html_content = driver.page_source
        print(f"📝 HTML长度: {len(html_content)} 字符")
        
        # 保存HTML文件（可选）
        html_file_path = None
        if save_html:
            from urllib.parse import urlparse
            import re
            
            # 从URL生成文件名
            parsed_url = urlparse(url)
            filename = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', parsed_url.netloc + parsed_url.path)
            html_file_path = f"{filename[:50]}.html"
            
            try:
                with open(html_file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"💾 HTML已保存到: {html_file_path}")
            except Exception as e:
                print(f"⚠️ HTML保存失败: {e}")
        
        # 使用 Trafilatura 提取内容
        print("🔍 使用 Trafilatura 提取内容...")
        
        # 基础文本提取
        extracted_text = trafilatura.extract(html_content)
        
        # 提取元数据
        metadata = trafilatura.extract_metadata(html_content)
        
        # 高级提取（包含更多选项）
        advanced_text = trafilatura.extract(
            html_content,
            favor_precision=True,    # 提高精确度
            favor_recall=False,      # 降低召回率，提高质量
            include_comments=False,  # 不包含评论
            include_tables=True,     # 包含表格
            include_formatting=True, # 保留基本格式
            include_links=False,     # 不包含链接
            include_images=False     # 不包含图片
        )
        
        # 提取结构化数据
        structured_data = trafilatura.extract(
            html_content,
            output_format='json',    # JSON格式输出
            include_formatting=True
        )
        
        # 组织返回结果
        result = {
            'success': True,
            'url': url,
            'page_title': page_title,
            'selenium_title': page_title,
            'extracted_title': metadata.title if metadata else page_title,
            'basic_text': extracted_text,
            'advanced_text': advanced_text,
            'structured_data': structured_data,
            'metadata': {
                'title': metadata.title if metadata else None,
                'author': metadata.author if metadata else None,
                'date': metadata.date if metadata else None,
                'description': metadata.description if metadata else None,
                'sitename': metadata.sitename if metadata else None,
                'language': metadata.language if metadata else None,
                'url': metadata.url if metadata else url
            },
            'statistics': {
                'html_length': len(html_content),
                'basic_text_length': len(extracted_text) if extracted_text else 0,
                'advanced_text_length': len(advanced_text) if advanced_text else 0,
                'has_content': bool(extracted_text and len(extracted_text) > 50)
            },
            'html_file_path': html_file_path,
            'processing_time': time.time()
        }
        
        # 输出提取结果摘要
        if extracted_text:
            print(f"✅ 内容提取成功!")
            print(f"   基础提取: {len(extracted_text)} 字符")
            print(f"   高级提取: {len(advanced_text) if advanced_text else 0} 字符")
            print(f"   提取标题: {result['extracted_title']}")
            print(f"   内容预览: {extracted_text[:100]}...")
        else:
            print(f"❌ 内容提取失败或内容为空")
            result['success'] = False
            result['error'] = '提取的内容为空'
        
        return result
        
    except Exception as e:
        error_msg = f"处理过程中出错: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'url': url
        }
    
    finally:
        # 如果是创建的新driver，则关闭它
        if driver_created and driver:
            try:
                driver.quit()
                print("🚪 已关闭WebDriver")
            except:
                pass

# 批量处理函数
def batch_selenium_trafilatura_extract(urls, driver=None, wait_time=3, max_urls=5):
    """
    批量处理多个URL
    
    Args:
        urls (list): URL列表
        driver: 共享的WebDriver对象
        wait_time (int): 每个页面的等待时间
        max_urls (int): 最大处理URL数量
    
    Returns:
        list: 处理结果列表
    """
    
    results = []
    urls_to_process = urls[:max_urls]
    
    print(f"🚀 开始批量处理 {len(urls_to_process)} 个URL")
    print("=" * 60)
    
    # 如果没有提供driver，创建一个共享的
    driver_created = False
    if driver is None:
        try:
            from selenium import webdriver
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            driver_created = True
            print("✅ 创建共享WebDriver")
        except Exception as e:
            print(f"❌ 无法创建WebDriver: {e}")
            return []
    
    try:
        for i, url in enumerate(urls_to_process, 1):
            print(f"\\n📍 处理第 {i}/{len(urls_to_process)} 个URL")
            print("-" * 40)
            
            result = selenium_trafilatura_extract(
                url, 
                driver=driver, 
                wait_time=wait_time, 
                save_html=False
            )
            
            results.append(result)
            
            # 避免过快请求
            if i < len(urls_to_process):
                time.sleep(1)
    
    finally:
        if driver_created and driver:
            driver.quit()
            print("\\n🚪 已关闭共享WebDriver")
    
    # 统计结果
    successful = sum(1 for r in results if r.get('success', False))
    print(f"\\n📊 批量处理完成: {successful}/{len(urls_to_process)} 成功")
    
    return results


def get_baidu_hot_news():
    # 优化Chrome启动配置，提高启动速度
    options = webdriver.ChromeOptions()
    # 基础性能优化选项
    options.add_argument('--headless') #不需要界面
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    # 网络和更新相关优化
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-component-update')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-extensions')
    # 日志和崩溃报告优化
    options.add_argument('--disable-logging')
    options.add_argument('--disable-crash-reporter')
    # 如果不需要界面可以启用无头模式（会更快）
    # options.add_argument('--headless')

    with open('selenium_log.txt', 'a', encoding='utf-8') as f:
        f.write("🚀 正在启动Chrome浏览器...\n")
    start_time = time.time()
    driver = webdriver.Chrome(options=options)
    end_time = time.time()
    with open('selenium_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"✅ Chrome启动完成，耗时: {end_time - start_time:.2f} 秒\n")

    driver.implicitly_wait(0.5)
    #进入首页找到热点页面
    #进入百度页面
    driver.get("https://www.baidu.com")
    # 使用CSS选择器定位a标签，然后获取href属性
    # 根据图片中的HTML结构，a标签有class="title-content tag-width c-link c-font-medium c-line-clamp1"
    #urls = driver.find_elements(by=By.CSS_SELECTOR, value="a.title-content.tag-width.c-link.c-font-medium.c-line-clamp1")
    urls = driver.find_elements(by=By.CSS_SELECTOR, value="a.title-content.c-link.c-font-medium.c-line-clamp1")
    #urls =urls+urls2
    specific_news = {}
    #获取百度首页的热点url列表
    hot_href_list = []  #每一个打开都是具体热点新闻页面
    hot_text_list = []
    specific_news = {}
    for url in urls:
        text = url.text
        href = url.get_attribute('href')
        hot_href_list.append(href)
        hot_text_list.append(text)
    href_value_list=[]
    for url,hot_text in zip(hot_href_list,hot_text_list):
        #打开热点列表中的一个
        driver.get(url)
        time.sleep(1)
        #获取"更多消息"的url
        # 获取页面第一个h3标签（class='t'），然后获取该h3标签中的a标签的href值
        #这是普通的查看更多消息url
        try:
                # 使用CSS选择器定位第一个class为't'的h3标签
            h3_element = driver.find_element(by=By.CSS_SELECTOR, value="h3.t")
            
            # 在h3标签内查找a标签
            a_element = h3_element.find_element(by=By.TAG_NAME, value="a")
            
            # 获取a标签的href属性值
            href_value = a_element.get_attribute('href')
            # href_value_list.append(href_value)
            with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                f.write(f'更多消息 {href_value}\n')
        except Exception as e:
            with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"获取元素时出错: {e}\n")
            href_value = None
        if href_value:
            driver.get(href_value)
            with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                f.write(f'进入热点{hot_text}页面\n')
            title = driver.title
            with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"更多消息页面标题: {title}\n")
            # 获取页面所有包含aria-label属性的元素
            elements_with_aria_label = driver.find_elements(by=By.CSS_SELECTOR, value="[aria-label]")

            with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"找到 {len(elements_with_aria_label)} 个包含aria-label属性的元素\n")
                f.write("=" * 80 + "\n")
            single_new_list=[]
            # 遍历每个元素并打印其原始HTML代码
            for i, element in enumerate(elements_with_aria_label, 1):
                # try:
                #     # 获取元素的aria-label属性值
                #     aria_label_value = element.get_attribute('aria-label')
                #     # 获取元素的原始HTML代码
                #     html_code = element.get_attribute('outerHTML')
                    
                #     # 将数据写入txt文件
                #     with open('aria_label_data.txt', 'a', encoding='utf-8') as f:
                #         f.write(f"元素 {i}:\n")
                #         f.write(f"aria-label值: {aria_label_value}\n")
                #         f.write(f"HTML代码: {html_code}\n")
                #         f.write("-" * 50 + "\n")
                # except Exception as e:
                #     print(f"处理第 {i} 个元素时出错: {e}")
                #     print("-" * 50)    
                # 检查元素结构，寻找a标签-span标签-span标签-span标签的模式
                if i >= 2:  # 从第三个元素开始检查
                    # 检查当前元素及其后3个元素是否形成a-span-span-span模式
                    if i + 3 <= len(elements_with_aria_label):  # 确保有足够的后续元素
                        current_element = element
                        next_element_1 = elements_with_aria_label[i]  # 当前元素
                        next_element_2 = elements_with_aria_label[i+1]  # 后一个元素
                        next_element_3 = elements_with_aria_label[i+2]  # 后两个元素
                        
                        # 检查标签类型
                        current_tag = current_element.tag_name
                        next_tag_1 = next_element_1.tag_name
                        next_tag_2 = next_element_2.tag_name
                        next_tag_3 = next_element_3.tag_name
                        
                        # 检查是否符合 a-span-span-span 的模式
                        if (current_tag == 'a' and next_tag_1 == 'span' and 
                            next_tag_2 == 'span' and next_tag_3 == 'span'):
                            
                            try:
                                # 获取第一个a标签的href和text
                                a_href = current_element.get_attribute('href')
                                a_text = current_element.text.strip()
                                
                                # 获取第二个span标签的aria-label值
                                second_span_aria_label = next_element_1.get_attribute('aria-label')
                                with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                                    f.write(f"{second_span_aria_label}\n")
                                
                                # 将符合条件的数据写入文件
                                with open('filtered_aria_label_data.txt', 'a', encoding='utf-8') as f:
                                    f.write(f"符合模式的元素组 {i//4}:\n")
                                    f.write(f"a标签href: {a_href}\n")
                                    f.write(f"a标签text: {a_text}\n")
                                    f.write(f"第二个span的aria-label: {second_span_aria_label}\n")
                                    f.write("=" * 50 + "\n")
                                
                                # print(f"找到符合模式的元素组 {i//4}: a标签href={a_href}, text={a_text}, 第二个span的aria-label={second_span_aria_label}")
                                if second_span_aria_label and (('天' in second_span_aria_label) or ('小时' in second_span_aria_label) or ('分钟' in second_span_aria_label)):
                                    with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                                        f.write('--加入列表--\n')
                                    single_new_list.append((href_value,a_text))
                            except Exception as e:
                                with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                                    f.write(f"处理符合模式的元素组时出错: {e}\n")
        if len(single_new_list)>0:
                specific_news[hot_text]=single_new_list
        else:
            with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                f.write(f'{hot_text}查看更多模式下没有找到符合循环模式的新闻url\n')
        #再次打开页面，获取查看完整新闻模式的url
        #打开热点列表中的一个
        single_new_list=[]
        driver.get(url)
        time.sleep(1)
        try:
            # 获取新页面中第一个有aria-label属性，且属性值中有'查看完整'的a标签中，取得a标签的href值
            elements_with_aria_label = driver.find_elements(by=By.CSS_SELECTOR, value="[aria-label]")
            # 查找第一个包含'查看完整'的a标签
            for element in elements_with_aria_label:
                aria_label_value = element.get_attribute('aria-label')
                tag_name = element.tag_name
                # 检查是否是a标签且aria-label包含'查看完整'
                if tag_name == 'a' and aria_label_value and '查看完整' in aria_label_value:
                    href_value = element.get_attribute('href')
                    with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                        f.write(f"找到包含'查看完整'的a标签，href: {href_value}\n")
                    break
            with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"查看完整模式下找到的新闻列表入口，href: {href_value}\n")
            if href_value:
                driver.get(href_value)
                time.sleep(1)
            # 获取页面所有class中含有content的a标签（class包含content但不一定完全等于content）
            elements_with_content_class = driver.find_elements(by=By.CSS_SELECTOR, value="a[class*='content']")
            for element in elements_with_content_class:
                href_value = element.get_attribute('href')
                text_content = element.text.strip()
                single_new_list.append((href_value,text_content))
                # class_value = element.get_attribute('class')
                # html_code = element.get_attribute('outerHTML')
                # with open('content_class_data.txt', 'a', encoding='utf-8') as f:
                #     f.write(f"元素 {i}:\n")
            if len(single_new_list)>0:
                    if hot_text in specific_news:
                        specific_news[hot_text]=specific_news[hot_text]+single_new_list
                    else:
                        specific_news[hot_text]=single_new_list
                    with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                        f.write(f'{hot_text}查看完整模式下找到符合循环模式的新闻url：\n{single_new_list}\n')
            else:
                with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                    f.write(f'{hot_text}查看更多模式下没有找到符合循环模式的新闻url\n')
        except Exception as e:
            with open('selenium_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"处理查看完整模式时出错: {e}\n")
    news_text = {}
    for key in specific_news.keys():
        print(f"=========处理{key}的新闻======")
        url_list =[]
        info_list =[]
        for href,text in specific_news[key]:
            url_list.append(href)
        for url in url_list:
            try:
                res = selenium_trafilatura_extract(url=url,driver=driver)
                #页面标题、文本、作者、网址、链接、日期、长度
                info_list.append((res['page_title'],res['advanced_text'],res['metadata']['author'],res['metadata']['sitename'],res['url'],res['metadata']['date'],res['statistics']['advanced_text_length']))
            except Exception as e:
                print(f" {e}")
        news_text[key] = info_list
    return news_text

def save_to_db(res,news_text):
    import datetime
    import json
    json_list =[json.loads(json_str.replace('```json\n', '').replace('\n```', '')) for json_str in res]
    # 准备插入数据的SQL语句 (PostgreSQL使用%s占位符)
    insert_sql = """
    INSERT INTO baidu_news (hottopic, page_title, content_text, author, site, url, update_time, content_length,absrtact,keywords)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s)
    """

    # 遍历news_text字典，将数据插入数据库
    i = 0
    for hottopic, news_list in news_text.items():     
        abstract = json_list[i].get('abstract', '无数据')
        keywords = json_list[i].get('keywords', '无数据')
        for news_item in news_list:
            try:
                # 解包元组数据
                page_title, content_text, author, site, url, update_time, content_length = news_item
                
                # 处理可能的None值
                page_title = page_title if page_title else ''
                content_text = content_text if content_text else ''
                author = author if author else ''
                site = site if site else ''
                url = url if url else ''
                
                # 特殊处理日期字段 - 确保是有效的日期格式或NULL
                if update_time and update_time.strip() and update_time != '':
                    # 如果有有效的日期，直接使用
                    processed_update_time = update_time
                else:
                    # 如果日期为空或无效，使用当前日期
                    processed_update_time = datetime.datetime.now().strftime('%Y-%m-%d')
                
                content_length = content_length if content_length else 0
                
                # 执行插入操作
                execute_query(insert_sql, (hottopic, page_title, content_text, author, site, url, processed_update_time, content_length,abstract,keywords))
                print(f"成功插入: {hottopic} - {page_title}")
                
                
            except Exception as e:
                print(f"插入失败 {hottopic}: {e}")
        i+=1

    print("数据插入完成！")




def get_topics(news_text):
    topics_list = []
    # news_text的列表有可能有空值
    for key in news_text.keys():
        info_list = news_text[key]
        #拼接文本
        raw_texts = ''
        for i,info in enumerate(info_list):
            # 检查info[1]是否为None，如果是则使用空字符串
            content_text = info[1] if info[1] is not None else ''
            if content_text:  # 只有当内容不为空时才添加
                raw_texts += f'第{i+1}篇：'+'\n'+content_text + '\n\n'
        #获取topics
        GET_TOPICS_PROMPT = """
        下面是关于“{key}”的一些新闻报道，根据这些新闻，进行新闻内容总结，总结内容不超过50字，并提取出5个主题关键词。
        返回json数据。
        示例返回形式：{"abstract":"人社部宣布，自从2025年6月起，个人养老金需要缴纳3%的个人所得税",
        "keywords":"民生，税务，政府，养老金，上调税率"}
        新闻报道是：{raw_texts}。
        你的回答：
        """
        GET_TOPICS_PROMPT = GET_TOPICS_PROMPT.replace('{key}',key)
        GET_TOPICS_PROMPT = GET_TOPICS_PROMPT.replace('{raw_texts}',raw_texts)
        #print('GET_TOPICS_PROMPT',GET_TOPICS_PROMPT)
        client = OpenAI(api_key=settings.DEEPSEEK_API, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content":GET_TOPICS_PROMPT },
        ],
        stream=False
        )
        system_msg = response.choices[0].message.content
        topics_list.append(system_msg)
    return topics_list
if __name__ == "__main__":
    news_text = get_baidu_hot_news()
    # 过滤掉空列表的情况
    filtered_news_text = {key: value for key, value in news_text.items() if value}
    res = get_topics(news_text)
    save_to_db(res,news_text)

        
