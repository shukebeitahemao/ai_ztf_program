# Cursor Python解释器配置指南

## 方法1：通过命令面板配置（推荐）

1. **打开命令面板**
   - 按 `Ctrl+Shift+P` (Windows/Linux) 或 `Cmd+Shift+P` (Mac)

2. **选择Python解释器**
   - 输入并选择: `Python: Select Interpreter`

3. **手动输入解释器路径**
   - 如果列表中没有显示虚拟环境，选择 "Enter interpreter path..."
   - 输入虚拟环境Python解释器的完整路径：
     ```
     D:\python_envs\ai_project\Scripts\python.exe
     ```

## 方法2：通过VSCode设置配置

1. **打开设置**
   - 按 `Ctrl+,` 打开设置
   - 或者点击 File → Preferences → Settings

2. **搜索Python路径**
   - 在搜索框输入 "python.pythonPath" 或 "python.defaultInterpreterPath"

3. **设置解释器路径**
   - 在设置中添加或修改:
     ```json
     {
         "python.defaultInterpreterPath": "D:\\python_envs\\ai_project\\Scripts\\python.exe"
     }
     ```

## 方法3：创建.vscode配置文件

在项目根目录创建 `.vscode/settings.json` 文件：

```json
{
    "python.pythonPath": "D:\\python_envs\\ai_project\\Scripts\\python.exe",
    "python.defaultInterpreterPath": "D:\\python_envs\\ai_project\\Scripts\\python.exe",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true
}
```

## 方法4：检查虚拟环境是否正确创建

打开终端确认虚拟环境存在：
```bash
# 检查Python解释器是否存在
ls D:\python_envs\ai_project\Scripts\python.exe

# 或者激活环境测试
D:\python_envs\ai_project\Scripts\activate
python --version
```

## 方法5：重新创建虚拟环境（如果需要）

如果虚拟环境有问题，可以重新创建：
```bash
# 删除旧环境
rmdir /s D:\python_envs\ai_project

# 重新创建
mkdir D:\python_envs
cd D:\python_envs
python -m venv ai_project

# 激活并安装依赖
D:\python_envs\ai_project\Scripts\activate
pip install -r D:\ai_ztf\requirements.txt
```

## 验证配置是否成功

1. **检查状态栏**
   - Cursor底部状态栏应该显示Python版本和虚拟环境名称

2. **打开Python文件**
   - 创建或打开.py文件，Cursor应该自动检测解释器

3. **运行代码测试**
   - 运行简单的Python代码确认环境正确

## 常见问题解决

### 问题1：权限不足
- 以管理员身份运行Cursor
- 检查虚拟环境目录权限

### 问题2：路径包含空格
- 使用双引号包围路径
- 或者重新在无空格路径创建虚拟环境

### 问题3：Python版本不匹配
- 确认虚拟环境Python版本
- 重新用正确版本创建虚拟环境

### 问题4：Cursor缓存问题
- 重启Cursor
- 清除Cursor缓存：`Ctrl+Shift+P` → "Developer: Reload Window" 