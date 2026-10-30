"""球员搜索 M3 网页版的 Windows 桌面外壳。

用 WebView2 加载 web/index.html，经 PyInstaller 打包成单文件 exe 分发。
打包前请先运行 python tools/build_web.py 生成 web/index.html。
"""

import os
import sys

WINDOW_TITLE = "球员搜索"


def html_path():
    candidates = []
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        candidates.append(os.path.join(bundle, "index.html"))
    here = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(here, "index.html"))
    candidates.append(os.path.join(os.path.dirname(here), "web", "index.html"))
    candidates.append(os.path.join(os.getcwd(), "web", "index.html"))
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("未找到 index.html，请先运行 python tools/build_web.py")


def create_window(webview_module, path=None):
    return webview_module.create_window(
        WINDOW_TITLE,
        "file://" + (path or html_path()),
        width=1100,
        height=780,
        min_size=(380, 600),
    )


def main():
    import webview
    create_window(webview)
    webview.start()


if __name__ == "__main__":
    main()
