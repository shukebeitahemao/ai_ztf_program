#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cursor Python环境自动修复脚本
"""

import os
import json
import subprocess
from pathlib import Path

def create_vscode_settings():
    """创建或更新.vscode/settings.json"""
    
    # 虚拟环境Python路径
    python_path = "D:\\python_envs\\ai_project\\Scripts\\python.exe"
    
    # 检查Python解释器是否存在
    if not Path(python_path).exists():
        print(f"❌ Python解释器不存在: {python_path}")
        print("请先创建虚拟环境:")
        print("mkdir D:\\python_envs")
        print("cd D:\\python_envs")
        print("python -m venv ai_project")
        return False
    
    # 创建.vscode目录
    vscode_dir = Path('.vscode')
    vscode_dir.mkdir(exist_ok=True)
    
    # 配置内容
    settings = {
        "python.pythonPath": python_path,
        "python.defaultInterpreterPath": python_path,
        "python.terminal.activateEnvironment": True,
        "python.terminal.activateEnvInCurrentTerminal": True,
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": False,
        "python.linting.flake8Enabled": True,
        "python.formatting.provider": "black",
        "python.analysis.typeCheckingMode": "basic",
        "files.encoding": "utf8",
        "files.autoSave": "afterDelay",
        "editor.formatOnSave": True,
        "[python]": {
            "editor.tabSize": 4,
            "editor.insertSpaces": True,
            "editor.defaultFormatter": "ms-python.python"
        }
    }
    
    # 写入配置文件
    settings_file = vscode_dir / 'settings.json'
    
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        
        print(f"✅ 已创建/更新配置文件: {settings_file}")
        return True
        
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False

def check_virtual_env():
    """检查虚拟环境状态"""
    
    python_path = Path("D:\\python_envs\\ai_project\\Scripts\\python.exe")
    
    if not python_path.exists():
        print("❌ 虚拟环境不存在，正在创建...")
        return create_virtual_env()
    else:
        print("✅ 虚拟环境已存在")
        return True

def create_virtual_env():
    """创建虚拟环境"""
    
    try:
        # 创建环境目录
        env_dir = Path("D:\\python_envs")
        env_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建虚拟环境
        subprocess.run([
            "python", "-m", "venv", 
            "D:\\python_envs\\ai_project"
        ], check=True)
        
        print("✅ 虚拟环境创建成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建虚拟环境失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 创建虚拟环境时出错: {e}")
        return False

def install_requirements():
    """安装项目依赖"""
    
    python_exe = "D:\\python_envs\\ai_project\\Scripts\\python.exe"
    pip_exe = "D:\\python_envs\\ai_project\\Scripts\\pip.exe"
    
    # 检查requirements.txt是否存在
    req_file = Path("requirements.txt")
    
    if req_file.exists():
        try:
            print("正在安装依赖...")
            subprocess.run([
                pip_exe, "install", "-r", "requirements.txt"
            ], check=True)
            print("✅ 依赖安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
    else:
        print("ℹ️  requirements.txt不存在，跳过依赖安装")
        
        # 安装基础包
        try:
            print("安装基础LlamaIndex包...")
            subprocess.run([
                pip_exe, "install", "llama-index"
            ], check=True)
            print("✅ 基础包安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 基础包安装失败: {e}")
            return False

def create_launch_config():
    """创建调试配置"""
    
    vscode_dir = Path('.vscode')
    vscode_dir.mkdir(exist_ok=True)
    
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "python": "D:\\python_envs\\ai_project\\Scripts\\python.exe"
            },
            {
                "name": "Python: Test Environment",
                "type": "python", 
                "request": "launch",
                "program": "${workspaceFolder}/test_python_env.py",
                "console": "integratedTerminal",
                "python": "D:\\python_envs\\ai_project\\Scripts\\python.exe"
            }
        ]
    }
    
    launch_file = vscode_dir / 'launch.json'
    
    try:
        with open(launch_file, 'w', encoding='utf-8') as f:
            json.dump(launch_config, f, indent=4, ensure_ascii=False)
        print(f"✅ 已创建调试配置: {launch_file}")
        return True
    except Exception as e:
        print(f"❌ 创建调试配置失败: {e}")
        return False

def main():
    """主修复流程"""
    
    print("=== Cursor Python环境自动修复 ===\n")
    
    # 1. 检查/创建虚拟环境
    print("1. 检查虚拟环境...")
    if not check_virtual_env():
        return
    
    # 2. 创建VSCode配置
    print("\n2. 创建VSCode配置...")
    if not create_vscode_settings():
        return
    
    # 3. 创建调试配置
    print("\n3. 创建调试配置...")
    create_launch_config()
    
    # 4. 安装依赖（可选）
    print("\n4. 安装依赖...")
    install_requirements()
    
    print("\n=== 修复完成 ===")
    print("\n接下来的步骤:")
    print("1. 重启Cursor")
    print("2. 按Ctrl+Shift+P，输入'Python: Select Interpreter'")
    print("3. 选择: D:\\python_envs\\ai_project\\Scripts\\python.exe")
    print("4. 运行 test_python_env.py 验证配置")
    
    print("\n如果仍有问题，请手动:")
    print("- 在Cursor中打开设置 (Ctrl+,)")
    print("- 搜索 'python.defaultInterpreterPath'")
    print("- 设置为: D:\\python_envs\\ai_project\\Scripts\\python.exe")

if __name__ == "__main__":
    main() 