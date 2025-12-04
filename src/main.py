import sys
import os
import tkinter as tk

# === 核心修复：强制设置搜索路径 ===
# 这一步必须在所有 from ... import ... 之前执行

# 1. 获取 main.py 所在的真实目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的 exe (PyInstaller)
    # sys._MEIPASS 是解压后的临时目录
    app_path = sys._MEIPASS
else:
    # 如果是本地源代码运行
    app_path = os.path.dirname(os.path.abspath(__file__))

# 2. 将该目录插入到系统搜索路径的【第一位】
# 使用 insert(0, ...) 确保优先加载我们自己的文件，而不是系统的同名库
if app_path not in sys.path:
    sys.path.insert(0, app_path)

# === 现在再导入其他模块，就一定能找到了 ===
try:
    from gui import CodeSyncApp
except ImportError as e:
    # 如果还是报错，弹窗提示路径信息，方便调试
    tk.messagebox.showerror("Startup Error",
        f"Failed to import modules.\n\nSearch Path:\n{sys.path}\n\nError:\n{e}")
    sys.exit(1)

def main():
    root = tk.Tk()
    app = CodeSyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()