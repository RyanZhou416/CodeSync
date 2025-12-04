import os
import sys
import platform

# 软件基础信息
APP_NAME = "CodeSync"

# 默认忽略文件
DEFAULT_IGNORE = {
    '.git', '.vs', '.idea', '__pycache__', 'node_modules',
    'build', 'target', 'bin', 'obj', '.gradle', '.dart_tool',
    '.vscode', '.DS_Store'
}

# 二进制文件后缀
BINARY_EXTS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.exe', '.dll', '.so',
    '.pdf', '.zip', '.db', '.sqlite', '.pyc', '.class', '.jar',
    '.webp', '.lib', '.pdb', '.o', '.a', '.mp4', '.mov'
}


def get_app_data_dir():
    """获取跨平台的应用配置存储目录"""
    system = platform.system()

    if system == "Windows":
        base = os.environ.get('APPDATA')
    elif system == "Darwin":  # macOS
        base = os.path.expanduser("~/Library/Application Support")
    else:  # Linux
        base = os.path.expanduser("~/.config")

    path = os.path.join(base, APP_NAME)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径。
    兼容开发环境(直接运行源码)和生产环境(PyInstaller打包后)。
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境：基于当前工作目录
    return os.path.join(os.path.abspath("."), relative_path)


# 全局路径常量
CONFIG_DIR = get_app_data_dir()
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# 语言文件路径 (相对于项目根目录/打包根目录)
LANG_FILE_REL = os.path.join("assets", "lang.json")


def get_version():
    """读取根目录的 VERSION 文件"""
    try:
        # 开发环境
        version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "VERSION")
        # 打包环境 (PyInstaller 会把 VERSION 打包进 sys._MEIPASS)
        if getattr(sys, 'frozen', False):
            version_file = os.path.join(sys._MEIPASS, "VERSION")

        with open(version_file, "r") as f:
            return f.read().strip()
    except:
        return "1.0.0"


APP_VERSION = get_version()