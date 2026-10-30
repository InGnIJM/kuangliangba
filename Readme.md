# Readme
## 项目介绍

这是一个球员搜索工具，可以根据球员的姓名、位置、联赛等条件进行搜索。开发于2026年春节，用于况两把活动中进行快速搜索。后续如果有类似活动仅需更新数据集即可继续使用。

提供三种形态：

| 形态 | 入口 | 说明 |
| --- | --- | --- |
| Windows 桌面版（旧） | `player_search.py` / `dist/player_search.exe` | tkinter 原版 |
| Windows 桌面版（新） | `dist/player_search_web.exe` | M3 网页界面，WebView2 外壳，单文件免安装 |
| 网页版 | `web/index.html` | 单文件、移动端自适应、实时筛选，浏览器直接打开 |
| 安卓 APP | `dist/player_search.apk`（debug）/ `dist/player_search-release.apk`（正式签名） | Capacitor 打包网页版，纯离线 |

## 如何使用

### 1、Windows 桌面版

直接运行 `player_search.py`，或打包成 exe：

```
pyinstaller -F -w player_search.py
```

### 2、网页版

```
python tools/build_web.py
```

生成 `web/index.html`（数据内嵌，单文件可双击打开，也可发到手机用浏览器打开）。

### 3、安卓 APK

debug 版（自己测试用）：

```
tools\build_apk.bat
```

release 版（分发给别人安装）：

```
tools\build_release.bat
```

产物分别为 `dist/player_search.apk` 与 `dist/player_search-release.apk`。

首次构建需准备环境（一次性）：

1. JDK 21（脚本默认 `C:\Program Files\Java\jdk-21`，不符请改 `tools/build_*.bat`）
2. `npm install`（安装 Capacitor 依赖）
3. 本目录下 `.android-sdk/`：放入 Android cmdline-tools 并安装 `platforms;android-36`、`build-tools`、`platform-tools`；`gradle-dist/` 放 Gradle 8.14.3 解压版（services.gradle.org 直连超时，可用腾讯镜像 `mirrors.cloud.tencent.com/gradle/`）
4. release 签名密钥：`.android-sdk/player_search.jks`（keytool 生成）+ `.android-sdk/ks-pass.txt`（密码文件）。**密钥文件不入库且不可丢失**，丢失后已安装的用户将无法覆盖升级

### 4、Windows M3 版 exe

```
tools\build_exe.bat
```

产物 `dist/player_search_web.exe`（单文件，内嵌网页数据，双击即用；需系统装有 WebView2 运行时，Win11 自带）。

首次构建需准备环境（一次性）：

```
python -m venv .venv-build
.venv-build\Scripts\pip install pywebview pyinstaller
```

## 数据集与分组更新

- 球员数据：`players.csv`（8 列：球员/位置/类型/背号/俱乐部/国籍/身高/惯用脚），换数据后重新运行 `build_web.py`（网页/APP）或重启桌面版
- 分组配置：`groups.json`，包含 `position_groups`（位置组别）、`league_groups`（联赛→俱乐部集合）、`country_continent`（国籍→大洲）三项，换数据集时按需修改，**不用改代码**
- 注意：`player_search.py` 桌面版仍使用代码内置分组，网页版/APP 读取 `groups.json`

## 测试

```
pytest test/ --cov=tools --cov-report=term-missing
```
