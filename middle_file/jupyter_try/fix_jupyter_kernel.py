#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复Jupyter Notebook无法识别虚拟环境内核的问题
"""

import subprocess
import sys
import json
import os
from pathlib import Path

def check_ipykernel_installation():
    """检查虚拟环境中是否安装了ipykernel"""
    
    venv_python = "D:\\python_envs\\ai_project\\Scripts\\python.exe"
    venv_pip = "D:\\python_envs\\ai_project\\Scripts\\pip.exe"
    
    print("=== 检查ipykernel安装状态 ===\n")
    
    # 检查虚拟环境是否存在
    if not Path(venv_python).exists():
        print(f"❌ 虚拟环境不存在: {venv_python}")
        return False
    
    # 检查ipykernel是否已安装
    try:
        result = subprocess.run([
            venv_python, "-c", "import ipykernel; print('ipykernel已安装')"
        ], capture_output=True, text=True, check=True)
        
        print("✅ ipykernel已安装")
        return True
        
    except subprocess.CalledProcessError:
        print("❌ ipykernel未安装，正在安装...")
        
        try:
            # 安装ipykernel
            subprocess.run([
                venv_pip, "install", "ipykernel"
            ], check=True)
            
            print("✅ ipykernel安装成功")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ ipykernel安装失败: {e}")
            return False

def register_kernel():
    """将虚拟环境注册为Jupyter内核"""
    
    venv_python = "D:\\python_envs\\ai_project\\Scripts\\python.exe"
    kernel_name = "ai_project"
    display_name = "Python (ai_project)"
    
    print(f"\n=== 注册Jupyter内核 ===\n")
    
    try:
        # 注册内核
        subprocess.run([
            venv_python, "-m", "ipykernel", "install", 
            "--user", 
            "--name", kernel_name,
            "--display-name", display_name
        ], check=True)
        
        print(f"✅ 内核注册成功")
        print(f"   内核名称: {kernel_name}")
        print(f"   显示名称: {display_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 内核注册失败: {e}")
        return False

def list_available_kernels():
    """列出所有可用的Jupyter内核"""
    
    print(f"\n=== 可用的Jupyter内核 ===\n")
    
    try:
        result = subprocess.run([
            "jupyter", "kernelspec", "list"
        ], capture_output=True, text=True, check=True)
        
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 无法列出内核: {e}")
        return False
    except FileNotFoundError:
        print("❌ jupyter命令未找到，请确保已安装Jupyter")
        return False

def install_jupyter_if_needed():
    """如果需要的话安装Jupyter"""
    
    print(f"\n=== 检查Jupyter安装 ===\n")
    
    # 检查jupyter是否已安装
    try:
        subprocess.run(["jupyter", "--version"], 
                      capture_output=True, check=True)
        print("✅ Jupyter已安装")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Jupyter未安装，正在安装...")
        
        try:
            # 在虚拟环境中安装Jupyter
            venv_pip = "D:\\python_envs\\ai_project\\Scripts\\pip.exe"
            subprocess.run([
                venv_pip, "install", "jupyter", "notebook", "jupyterlab"
            ], check=True)
            
            print("✅ Jupyter安装成功")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Jupyter安装失败: {e}")
            return False

def create_kernel_spec_manually():
    """手动创建内核规格文件"""
    
    print(f"\n=== 手动创建内核规格 ===\n")
    
    # 获取用户数据目录
    if os.name == 'nt':  # Windows
        kernel_dir = Path.home() / "AppData" / "Roaming" / "jupyter" / "kernels" / "ai_project"
    else:  # Linux/Mac
        kernel_dir = Path.home() / ".local" / "share" / "jupyter" / "kernels" / "ai_project"
    
    # 创建内核目录
    kernel_dir.mkdir(parents=True, exist_ok=True)
    
    # 内核规格内容
    kernel_spec = {
        "argv": [
            "D:\\python_envs\\ai_project\\Scripts\\python.exe",
            "-m",
            "ipykernel_launcher",
            "-f",
            "{connection_file}"
        ],
        "display_name": "Python (ai_project)",
        "language": "python",
        "metadata": {
            "debugger": True
        }
    }
    
    # 写入kernel.json文件
    kernel_file = kernel_dir / "kernel.json"
    
    try:
        with open(kernel_file, 'w', encoding='utf-8') as f:
            json.dump(kernel_spec, f, indent=2)
        
        print(f"✅ 手动创建内核规格成功")
        print(f"   内核目录: {kernel_dir}")
        print(f"   规格文件: {kernel_file}")
        return True
        
    except Exception as e:
        print(f"❌ 手动创建内核规格失败: {e}")
        return False

def test_jupyter_notebook():
    """测试Jupyter Notebook是否能正常工作"""
    
    print(f"\n=== 测试Jupyter Notebook ===\n")
    
    try:
        # 创建测试notebook
        test_nb_content = {
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "import sys\n",
                        "print(f'Python解释器: {sys.executable}')\n",
                        "print(f'Python版本: {sys.version}')\n",
                        "\n",
                        "# 检查是否在虚拟环境中\n",
                        "import os\n",
                        "venv_path = os.environ.get('VIRTUAL_ENV')\n",
                        "if venv_path:\n",
                        "    print(f'虚拟环境: {venv_path}')\n",
                        "else:\n",
                        "    print('未检测到虚拟环境')\n",
                        "\n",
                        "# 测试LlamaIndex导入\n",
                        "try:\n",
                        "    import llama_index\n",
                        "    print('✅ LlamaIndex可用')\n",
                        "except ImportError:\n",
                        "    print('❌ LlamaIndex不可用')"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python (ai_project)",
                    "language": "python",
                    "name": "ai_project"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.x"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        # 保存测试notebook
        test_nb_file = Path("test_kernel.ipynb")
        with open(test_nb_file, 'w', encoding='utf-8') as f:
            json.dump(test_nb_content, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 创建测试notebook: {test_nb_file}")
        print("请在Cursor中打开此文件，选择ai_project内核进行测试")
        return True
        
    except Exception as e:
        print(f"❌ 创建测试notebook失败: {e}")
        return False

def create_activation_script():
    """创建激活虚拟环境并启动Jupyter的脚本"""
    
    print(f"\n=== 创建启动脚本 ===\n")
    
    # Windows批处理脚本
    bat_script = """@echo off
echo 启动AI项目Jupyter环境...
echo.

REM 激活虚拟环境
call D:\\python_envs\\ai_project\\Scripts\\activate

REM 显示环境信息
echo 当前虚拟环境: %VIRTUAL_ENV%
echo 当前目录: %CD%
echo.

REM 启动Jupyter Lab
echo 启动Jupyter Lab...
jupyter lab

pause
"""
    
    bat_file = Path("start_jupyter.bat")
    try:
        with open(bat_file, 'w', encoding='utf-8') as f:
            f.write(bat_script)
        print(f"✅ 创建Windows启动脚本: {bat_file}")
    except Exception as e:
        print(f"❌ 创建Windows启动脚本失败: {e}")
    
    # Shell脚本
    sh_script = """#!/bin/bash
echo "启动AI项目Jupyter环境..."
echo

# 激活虚拟环境
source D:/python_envs/ai_project/Scripts/activate

# 显示环境信息
echo "当前虚拟环境: $VIRTUAL_ENV"
echo "当前目录: $(pwd)"
echo

# 启动Jupyter Lab
echo "启动Jupyter Lab..."
jupyter lab
"""
    
    sh_file = Path("start_jupyter.sh")
    try:
        with open(sh_file, 'w', encoding='utf-8') as f:
            f.write(sh_script)
        
        # 给shell脚本执行权限
        if not os.name == 'nt':
            os.chmod(sh_file, 0o755)
            
        print(f"✅ 创建Shell启动脚本: {sh_file}")
    except Exception as e:
        print(f"❌ 创建Shell启动脚本失败: {e}")

def main():
    """主修复流程"""
    
    print("=== Jupyter Notebook内核修复工具 ===\n")
    
    # 1. 安装Jupyter（如果需要）
    if not install_jupyter_if_needed():
        return
    
    # 2. 检查并安装ipykernel
    if not check_ipykernel_installation():
        return
    
    # 3. 注册内核
    print("\n正在注册内核...")
    if not register_kernel():
        print("尝试手动创建内核规格...")
        create_kernel_spec_manually()
    
    # 4. 列出可用内核
    list_available_kernels()
    
    # 5. 创建测试notebook
    test_jupyter_notebook()
    
    # 6. 创建启动脚本
    create_activation_script()
    
    print(f"\n=== 修复完成 ===")
    print(f"\n接下来的步骤:")
    print(f"1. 重启Cursor")
    print(f"2. 打开或创建一个.ipynb文件")
    print(f"3. 点击右上角的内核选择器")
    print(f"4. 选择 'Python (ai_project)' 内核")
    print(f"5. 运行测试代码验证")
    
    print(f"\n或者使用启动脚本:")
    print(f"- 双击 start_jupyter.bat (Windows)")
    print(f"- 运行 ./start_jupyter.sh (Linux/Mac)")

if __name__ == "__main__":
    main() 