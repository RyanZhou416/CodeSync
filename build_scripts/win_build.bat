@echo off
echo Start Building CodeSync for Windows...

:: 确保在项目根目录运行 (如果脚本在 build_scripts 里，需要切到上一级)
cd /d "%~dp0.."

:: 清理旧构建
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: 运行 PyInstaller
:: --noconsole: 不显示黑框
:: --onefile: 生成单文件 exe
:: --name: 指定文件名
:: 注意：这里没有使用 --add-data，因为我们要把 lang.json 作为外部资源文件，方便你修改
pyinstaller --noconsole --onefile --name "CodeSync" src/main.py

echo.
echo Build finished! Check the 'dist' folder.
echo You can now compile 'build_scripts/win_setup.iss' to create the installer.
pause