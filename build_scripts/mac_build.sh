#!/bin/bash

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 清理
rm -rf dist build *.spec

echo "Building CodeSync for macOS..."

# 生成 .app
# 注意：macOS 下通常建议把资源打包进 .app 内部，这里我们用 --add-data
# 格式 source:dest
# 如果你有 icon.icns，取消注释 --icon 参数
pyinstaller --noconsole --windowed --name "CodeSync" \
    --add-data "assets/lang.json:assets" \
    src/main.py
    # --icon "assets/icon.icns" \

echo "Build complete. Check 'dist/CodeSync.app'"