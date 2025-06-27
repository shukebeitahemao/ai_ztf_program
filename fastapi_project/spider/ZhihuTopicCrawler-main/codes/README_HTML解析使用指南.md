# 知乎HTML页面解析脚本使用指南

## 📋 功能描述

这个脚本用于解析知乎热门问题页面HTML，提取问题的关键信息并保存到CSV文件中。

## 🎯 解析目标

从HTML页面的每个`<section class="HotItem">`中提取：

- **title**: 问题标题 (从`<h2 class="HotItem-title">`提取)
- **id**: 问题ID (从URL中提取数字部分)
- **url**: 完整问题链接
- **abstract**: 问题摘要 (从`<p class="HotItem-excerpt">`提取)
- **hot**: 热度信息 (如"880万热度")
- **type**: 固定为"热点问题"
- **date**: 当前日期 (格式: YYYY-MM-DD)

## 🚀 使用方法

### 1. 环境准备

确保安装了必要的依赖：
```bash
pip install beautifulsoup4 pandas requests
```

### 2. 文件准备

- 将要解析的HTML文件命名为`text.html`，放在`codes/`目录下
- 确保`get_url_text.py`文件在同一目录

### 3. 运行脚本

```bash
cd fastapi_project/spider/ZhihuTopicCrawler-main/codes
python parse_html.py
```

### 4. 查看结果

解析结果会保存到`../data/hot_questions.csv`文件中。

## 📊 输出格式

CSV文件包含以下列：
```
type,id,title,url,date,hot,abstract
热点问题,1919032669615912434,北京电子科技学院、国防科技大学等多所高校明确不招复读生...,https://www.zhihu.com/question/1919032669615912434,2025-06-20,880万热度,北京电子科技学院 北京电子科技学院 2025 年本科招生章程指出...
```

## 🔧 脚本特性

### ✅ 智能提取
- 使用BeautifulSoup进行HTML解析
- 正则表达式提取问题ID和热度信息
- 自动清理文本格式（去除多余空白字符）

### ✅ 错误处理
- 文件不存在检查
- 元素缺失容错处理
- 详细的解析过程日志

### ✅ 数据验证
- 保存后自动验证文件
- 显示文件大小和内容预览
- 完整的执行状态反馈

## 📝 解析示例

### 输入HTML结构：
```html
<section class="HotItem">
    <div class="HotItem-content">
        <a href="https://www.zhihu.com/question/1919032669615912434">
            <h2 class="HotItem-title">问题标题</h2>
            <p class="HotItem-excerpt">问题摘要内容...</p>
        </a>
        <div class="HotItem-metrics">880 万热度</div>
    </div>
</section>
```

### 输出CSV记录：
```csv
热点问题,1919032669615912434,问题标题,https://www.zhihu.com/question/1919032669615912434,2025-06-20,880万热度,问题摘要内容...
```

## ⚠️ 注意事项

1. **HTML文件格式**: 确保HTML文件使用UTF-8编码
2. **目录结构**: 脚本会自动创建输出目录
3. **重复内容**: 如果HTML中有重复的section，会生成多行相同数据
4. **缺失元素**: 如果某些元素不存在，对应字段会为空

## 🔍 故障排除

### 问题1: 找不到HTML文件
**解决**: 确保`text.html`文件在`codes/`目录下

### 问题2: 解析结果为空
**解决**: 检查HTML文件中是否包含`<section class="HotItem">`元素

### 问题3: 编码错误
**解决**: 确保HTML文件使用UTF-8编码保存

### 问题4: 依赖包缺失
**解决**: 运行`pip install beautifulsoup4 pandas requests`

## 📈 扩展功能

脚本可以轻松扩展来解析其他类型的HTML页面，只需要修改：
- CSS选择器
- 正则表达式模式
- 输出字段定义

## 🎉 成功示例

运行成功后会看到类似输出：
```
🚀 开始执行知乎热门问题HTML解析脚本
📊 找到 2 个热门问题section
✅ 成功保存 2 条记录到: ../data/hot_questions.csv
🎉 脚本执行完成！ 