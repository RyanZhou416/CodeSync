@echo off
setlocal

echo ==============================================
echo      CodeSync Windows Builder (Fixed)
echo ==============================================

:: 1. 切换到项目根目录
cd /d "%~dp0.."
echo Current Work Dir: %cd%

:: 2. 智能检测虚拟环境
if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
    echo [INFO] Using virtual environment: .venv
) else if exist "venv\Scripts\python.exe" (
    set "PY_CMD=venv\Scripts\python.exe"
    echo [INFO] Using virtual environment: venv
) else (
    set "PY_CMD=python"
    echo [WARN] Using system Python.
)

:: 3. 确保安装了 PyInstaller
echo.
echo [1/4] Checking PyInstaller...
"%PY_CMD%" -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install PyInstaller.
    pause
    exit /b 1
)

:: 4. 清理旧构建
echo.
echo [2/4] Cleaning up...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "CodeSync.spec" del "CodeSync.spec"

:: 5. 执行打包 (核心修改在这里)
:: --paths "src": 告诉 PyInstaller 去 src 目录下找 import 的模块
echo.
echo [3/4] Building EXE...
"%PY_CMD%" -m PyInstaller --noconsole --onefile --name "CodeSync" --clean ^
    --paths "src" ^
    --add-data "assets/lang.json;assets" ^
    --add-data "VERSION;." ^
    src/main.py

:: 6. 检查结果
echo.
if exist "dist\CodeSync.exe" (
    echo [4/4] Build Success!
    echo ------------------------------------------
    echo EXE Location: dist\CodeSync.exe
    echo.
    echo Now you can run 'build_scripts\win_setup.iss' to create the installer.
) else (
    echo [ERROR] Build Failed! Check the log above.
)

echo.
pause