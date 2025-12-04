import sys
import os
import tkinter as tk

# === 核心修复 1: 确保 Python 能找到同级目录下的模块 ===
# 获取当前 main.py 所在的目录 (即 src 目录)
if getattr(sys, 'frozen', False):
    # 如果是打包后的 exe 环境
    current_dir = sys._MEIPASS
else:
    # 如果是本地代码运行环境
    current_dir = os.path.dirname(os.path.abspath(__file__))

# 将此目录加入系统路径，这样就可以直接 import gui, config 等
sys.path.append(current_dir)

# === 核心修复 2: 去掉相对引用的点 (.) ===
# 修改前: from .gui import CodeSyncApp
# 修改后:
from gui import CodeSyncApp

def main():
    root = tk.Tk()
    app = CodeSyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()