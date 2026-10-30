@echo off
rem 构建安卓 debug APK：web/index.html -> dist/player_search.apk
rem 前置：JDK 21、.android-sdk（见 Readme）、npm install、npx cap add android
setlocal
cd /d "%~dp0.."

set "JAVA_HOME=C:\Program Files\Java\jdk-21"
set "ANDROID_HOME=%CD%\.android-sdk"
set "ANDROID_SDK_ROOT=%ANDROID_HOME%"
set "GRADLE=%ANDROID_HOME%\gradle-dist\gradle-8.14.3\bin\gradle.bat"

if not exist web\index.html (
    echo [1/3] 生成 web\index.html ...
    python tools\build_web.py || exit /b 1
) else (
    echo [1/3] web\index.html 已存在（如需更新请先运行 python tools\build_web.py）
)

if not exist android (
    echo [2/3] 初始化 Capacitor Android 工程 ...
    call npx cap add android || exit /b 1
) else (
    echo [2/3] 同步 web 资源到 Android 工程 ...
    call npx cap sync android || exit /b 1
)

echo [3/3] Gradle 编译 APK ...
cd android
call "%GRADLE%" assembleDebug || exit /b 1
cd ..

copy /y android\app\build\outputs\apk\debug\app-debug.apk dist\player_search.apk >nul
echo 完成: dist\player_search.apk
endlocal
