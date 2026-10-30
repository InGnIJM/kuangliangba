@echo off
rem 构建 release 签名 APK：web/index.html -> dist/player_search-release.apk
rem 前置：JDK 21、.android-sdk（含 player_search.jks 与 ks-pass.txt）、npm install、android 工程已生成
setlocal
cd /d "%~dp0.."

set "JAVA_HOME=C:\Program Files\Java\jdk-21"
set "ANDROID_HOME=%CD%\.android-sdk"
set "ANDROID_SDK_ROOT=%ANDROID_HOME%"
set "GRADLE=%ANDROID_HOME%\gradle-dist\gradle-8.14.3\bin\gradle.bat"

if not exist web\index.html (
    echo [1/4] 生成 web\index.html ...
    python tools\build_web.py || exit /b 1
) else (
    echo [1/4] web\index.html 已存在（如需更新请先运行 python tools\build_web.py）
)

echo [2/4] 同步 web 资源到 Android 工程 ...
call npx cap sync android || exit /b 1

echo [3/4] Gradle 编译 release ...
cd android
call "%GRADLE%" assembleRelease || exit /b 1
cd ..

echo [4/4] zipalign + 签名 ...
for /d %%d in (.android-sdk\build-tools\*) do set "BT=%%d"
"%BT%\zipalign.exe" -p -f 4 android\app\build\outputs\apk\release\app-release-unsigned.apk dist\_aligned.apk || exit /b 1
call "%BT%\apksigner.bat" sign --ks .android-sdk\player_search.jks --ks-key-alias player_search --ks-pass file:.android-sdk\ks-pass.txt --out dist\player_search-release.apk dist\_aligned.apk || exit /b 1
del /q dist\_aligned.apk dist\player_search-release.apk.idsig 2>nul
echo 完成: dist\player_search-release.apk
endlocal
