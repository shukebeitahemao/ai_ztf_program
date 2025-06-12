from prompt import GET_KG_PROMPT

# 测试文本
test_text = "今天下午，张三在公园遇到了李四，两人相谈甚欢。"

# 直接使用f-string的变量替换
formatted_prompt = GET_KG_PROMPT.replace("{txt}", test_text)

print("格式化后的提示词：")
print(formatted_prompt) 