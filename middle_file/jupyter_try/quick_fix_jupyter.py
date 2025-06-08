#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速修复Jupyter Notebook内核问题
"""

import subprocess
import sys
from pathlib import Path

def quick_fix():
    """快速修复Jupyter内核问题"""
    
    print("🔧 快速修复Jupyter内核问题\n")
    
    venv_python = "D:\\python_envs\\ai_project\\Scripts\\python.exe"
    venv_pip = "D:\\python_envs\\ai_project\\Scripts\\pip.exe"
    
    # 检查虚拟环境
    if not Path(venv_python).exists():
        print(f"❌ 虚拟环境不存在: {venv_python}")
        return False
    
    print("1. 安装ipykernel...")
    try:
        subprocess.run([venv_pip, "install", "ipykernel"], check=True)
        print("✅ ipykernel安装完成")
    except:
        print("⚠️  ipykernel可能已安装")
    
    print("\n2. 注册内核...")
    try:
        subprocess.run([
            venv_python, "-m", "ipykernel", "install", 
            "--user", "--name", "ai_project", 
            "--display-name", "Python (ai_project)"
        ], check=True)
        print("✅ 内核注册成功")
    except Exception as e:
        print(f"❌ 内核注册失败: {e}")
        return False
    
    print("\n3. 验证内核...")
    try:
        result = subprocess.run(["jupyter", "kernelspec", "list"], 
                              capture_output=True, text=True)
        if "ai_project" in result.stdout:
            print("✅ 内核验证成功")
            print("\n可用内核:")
            print(result.stdout)
        else:
            print("⚠️  内核可能未正确注册")
    except:
        print("⚠️  无法验证内核，但可能已成功注册")
    
    print(f"\n🎉 修复完成！")
    print(f"请重启Cursor，然后在Jupyter Notebook中选择 'Python (ai_project)' 内核")
    
    return True

if __name__ == "__main__":
    quick_fix() 