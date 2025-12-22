#!/bin/bash

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 清理
rm -rf dist build *.spec

echo "Building CodeSync for Linux..."

# 生成二进制文件
# Linux 下我们也把资源打包进去，方便单文件分发
pyinstaller --noconsole --onefile --name "CodeSync" \
    --add-data "assets:assets" \
    src/main.py

echo "Build complete. Check 'dist/CodeSync'"