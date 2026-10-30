@echo off
rem 打包 M3 网页版为单文件 exe：web/index.html -> dist/player_search_web.exe
rem 前置：.venv-build（见 Readme）
setlocal
cd /d "%~dp0.."

if not exist .venv-build\Scripts\pyinstaller.exe (
    echo 缺少 .venv-build 环境，请先执行：
    echo   python -m venv .venv-build
    echo   .venv-build\Scripts\pip install pywebview pyinstaller
    exit /b 1
)

if not exist web\index.html (
    python tools\build_web.py || exit /b 1
)

.venv-build\Scripts\pyinstaller.exe -F -w -n "player_search_web" ^
    --add-data "%CD%\web\index.html;." ^
    --collect-all webview --collect-all pythonnet --collect-all clr_loader --collect-all cffi ^
    --distpath dist --workpath build\exe --specpath build -y tools\app_webview.py || exit /b 1

echo 完成: dist\player_search_web.exe
endlocal
