#!/bin/bash

# 1. 切换到项目根目录 (脚本位于 build_scripts，所以向上一级)
cd "$(dirname "$0")/.."
echo "Current Work Dir: $(pwd)"

# 2. 清理旧的构建文件
echo "Cleaning up old build artifacts..."
rm -rf dist build *.spec

# 3. (可选) 安装依赖 - 如果你确定本地环境已就绪，可以注释掉这两行
echo "Checking dependencies..."
pip3 install -r requirements.txt
pip3 install pyinstaller

echo "Building CodeSync for macOS..."

# 4. 生成 .app
# --paths "src": 告诉 PyInstaller 去 src 目录找模块
# --hidden-import: 强制打包这些模块，防止漏掉
# --add-data "src:dest": macOS/Linux 使用冒号分隔
# --icon: 如果你有 assets/icon.icns，请取消注释那一行

pyinstaller --noconsole --windowed --name "CodeSync" --clean \
    --paths "src" \
    --hidden-import gui \
    --hidden-import logic \
    --hidden-import config \
    --hidden-import utils \
    --add-data "assets/lang.json:assets" \
    --add-data "VERSION:." \
    --icon "assets/icon.icns" \
    src/main.py


echo "------------------------------------------"
if [ -d "dist/CodeSync.app" ]; then
    echo "✅ Build Success!"
    echo "App located at: dist/CodeSync.app"
else
    echo "❌ Build Failed!"
    exit 1
fi