import os
import sys
import platform

# 软件基础信息
APP_NAME = "CodeSync"

# === 新增：安全相关的常量 ===
# 用于识别 CodeSync 生成的文件的魔法头（第一行）
MAGIC_HEADER = "# CodeSync Context File"
# 默认时间格式 (文件名安全格式)
DATE_FMT_FILE = "%Y-%m-%d_%H-%M-%S"
# 内部记录用的时间格式
DATE_FMT_LOG = "%Y-%m-%d %H:%M:%S"

# 默认忽略文件
DEFAULT_IGNORE = {
    '.git', '.vs', '.idea', '__pycache__', 'node_modules',
    'build', 'target', 'bin', 'obj', '.gradle', '.dart_tool',
    '.vscode', '.DS_Store', 'dist', 'venv', '.venv'
}

# 二进制文件后缀
BINARY_EXTS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.exe', '.dll', '.so',
    '.pdf', '.zip', '.db', '.sqlite', '.pyc', '.class', '.jar',
    '.webp', '.lib', '.pdb', '.o', '.a', '.mp4', '.mov', '.woff', '.woff2'
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
    """获取资源文件的绝对路径 (兼容 PyInstaller)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 全局路径常量
CONFIG_DIR = get_app_data_dir()
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LANG_FILE_REL = os.path.join("assets", "lang.json")

def get_version():
    """读取根目录的 VERSION 文件"""
    try:
        # 开发环境
        version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "VERSION")
        # 打包环境
        if getattr(sys, 'frozen', False):
            version_file = os.path.join(sys._MEIPASS, "VERSION")

        with open(version_file, "r") as f:
            return f.read().strip()
    except:
        return "1.0.0"

APP_VERSION = get_version()