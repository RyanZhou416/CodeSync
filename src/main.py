import sys
import os
import tkinter as tk
import tkinter.messagebox  # 显式导入


# === 核心路径修复 ===
def setup_path():
    """强制将当前运行目录加入系统路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 exe (PyInstaller)
        # 资源文件会被解压到 sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # 如果是本地代码运行
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 将该目录插入到 sys.path 的最前面
    if base_path not in sys.path:
        sys.path.insert(0, base_path)

    return base_path


# 1. 先执行路径设置
current_path = setup_path()

# 2. 然后再导入同级模块
try:
    # 直接 import，不要用 .gui
    from gui import CodeSyncApp
except ImportError as e:
    # 如果出错，显示详细的调试信息
    root = tk.Tk()
    root.withdraw()
    err_msg = f"启动错误: {e}\n\nSearch Path:\n{sys.path}\n\nBase Path:\n{current_path}"
    tkinter.messagebox.showerror("Error", err_msg)
    sys.exit(1)


def main():
    root = tk.Tk()
    app = CodeSyncApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()