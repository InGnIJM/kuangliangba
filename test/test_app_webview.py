import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import app_webview


class TestHtmlPath:
    def test_prefers_bundled_meipass(self, tmp_path, monkeypatch):
        bundled = tmp_path / "index.html"
        bundled.write_text("x", encoding="utf-8")
        monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
        assert app_webview.html_path() == str(bundled)

    def test_falls_back_to_repo_web_dir(self, tmp_path, monkeypatch):
        monkeypatch.delattr(sys, "_MEIPASS", raising=False)
        fake_tools = tmp_path / "tools"
        fake_tools.mkdir()
        (tmp_path / "web").mkdir()
        target = tmp_path / "web" / "index.html"
        target.write_text("x", encoding="utf-8")
        monkeypatch.setattr(app_webview, "__file__", str(fake_tools / "app_webview.py"))
        monkeypatch.chdir(tmp_path)
        assert app_webview.html_path() == str(target)

    def test_raises_when_missing(self, tmp_path, monkeypatch):
        monkeypatch.delattr(sys, "_MEIPASS", raising=False)
        monkeypatch.setattr(app_webview, "__file__", str(tmp_path / "tools" / "app_webview.py"))
        monkeypatch.chdir(tmp_path)
        with pytest.raises(FileNotFoundError):
            app_webview.html_path()


class TestCreateWindow:
    def test_creates_window_with_file_url(self, tmp_path):
        fake = MagicMock()
        html = tmp_path / "index.html"
        html.write_text("x", encoding="utf-8")
        app_webview.create_window(fake, str(html))
        args, kwargs = fake.create_window.call_args
        assert args[0] == app_webview.WINDOW_TITLE
        assert args[1].startswith("file://")
        assert str(html) in args[1]


class TestMain:
    def test_main_starts_webview(self, tmp_path, monkeypatch):
        fake = MagicMock()
        monkeypatch.setitem(sys.modules, "webview", fake)
        html = tmp_path / "index.html"
        html.write_text("x", encoding="utf-8")
        monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
        app_webview.main()
        fake.create_window.assert_called_once()
        fake.start.assert_called_once()

    def test_script_entrypoint(self, tmp_path, monkeypatch):
        import runpy
        fake = MagicMock()
        monkeypatch.setitem(sys.modules, "webview", fake)
        html = tmp_path / "index.html"
        html.write_text("x", encoding="utf-8")
        monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
        runpy.run_path(str(Path(app_webview.__file__).resolve()), run_name="__main__")
        fake.start.assert_called_once()
