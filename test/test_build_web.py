import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import build_web


CSV_HEADER = "球员,位置,类型,背号,俱乐部,国籍,身高,惯用脚\n"


def write_csv(path, rows):
    lines = [CSV_HEADER]
    for r in rows:
        lines.append(",".join(r) + "\n")
    path.write_text("".join(lines), encoding="utf-8")


def write_groups(path, **overrides):
    cfg = {
        "position_groups": {"全部": [], "前场": ["中锋"]},
        "league_groups": {"全部": [], "英超": ["曼联"]},
        "country_continent": {"法国": "欧洲"},
    }
    cfg.update(overrides)
    path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    return cfg


class TestLoadPlayers:
    def test_loads_rows_with_all_fields(self, tmp_path):
        csv_path = tmp_path / "players.csv"
        write_csv(csv_path, [["梅西", "右边锋", "现役", "30", "迈阿密", "阿根廷", "170", "左"]])
        players = build_web.load_players(csv_path)
        assert players == [{
            "球员": "梅西", "位置": "右边锋", "类型": "现役", "背号": "30",
            "俱乐部": "迈阿密", "国籍": "阿根廷", "身高": "170", "惯用脚": "左",
        }]

    def test_normalizes_whitespace(self, tmp_path):
        csv_path = tmp_path / "players.csv"
        write_csv(csv_path, [[" 梅 西 ", "右边锋", "现役", "30", "迈阿密", "阿根廷", "170", "左"]])
        players = build_web.load_players(csv_path)
        assert players[0]["球员"] == "梅西"

    def test_handles_utf8_sig(self, tmp_path):
        csv_path = tmp_path / "players.csv"
        csv_path.write_text(CSV_HEADER + "梅西,右边锋,现役,30,迈阿密,阿根廷,170,左\n",
                            encoding="utf-8-sig")
        players = build_web.load_players(csv_path)
        assert players[0]["球员"] == "梅西"

    def test_missing_column_becomes_empty(self, tmp_path):
        csv_path = tmp_path / "players.csv"
        csv_path.write_text("球员,位置\n梅西,右边锋\n", encoding="utf-8")
        players = build_web.load_players(csv_path)
        assert players[0]["俱乐部"] == "" and players[0]["背号"] == ""

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            build_web.load_players(tmp_path / "nope.csv")


class TestLoadGroups:
    def test_loads_config(self, tmp_path):
        path = tmp_path / "groups.json"
        cfg = write_groups(path)
        assert build_web.load_groups(path) == cfg

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            build_web.load_groups(tmp_path / "nope.json")

    def test_invalid_json_raises(self, tmp_path):
        path = tmp_path / "groups.json"
        path.write_text("{bad json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            build_web.load_groups(path)

    def test_missing_key_raises(self, tmp_path):
        path = tmp_path / "groups.json"
        path.write_text(json.dumps({"position_groups": {}}), encoding="utf-8")
        with pytest.raises(KeyError):
            build_web.load_groups(path)


class TestEmbedJson:
    def test_produces_valid_json(self):
        assert json.loads(build_web.embed_json({"a": 1})) == {"a": 1}

    def test_escapes_closing_script_tag(self):
        out = build_web.embed_json({"x": "</script><script>"})
        assert "</script>" not in out
        assert "<\\/script>" in out

    def test_unicode_not_escaped(self):
        assert "梅西" in build_web.embed_json({"n": "梅西"})


class TestBuildHtml:
    def test_replaces_placeholders(self, tmp_path):
        tpl = "DATA=__PLAYERS_JSON__;CFG=__CONFIG_JSON__;"
        html = build_web.build_html(tpl, [{"球员": "a"}], {"k": 1})
        assert "__PLAYERS_JSON__" not in html
        assert "__CONFIG_JSON__" not in html
        assert '"球员":"a"' in html
        assert '"k":1' in html


class TestMain:
    def test_generates_output(self, tmp_path):
        csv_path = tmp_path / "players.csv"
        groups_path = tmp_path / "groups.json"
        tpl_path = tmp_path / "tpl.html"
        out_path = tmp_path / "web" / "index.html"
        write_csv(csv_path, [["梅西", "右边锋", "现役", "30", "迈阿密", "阿根廷", "170", "左"]])
        write_groups(groups_path)
        tpl_path.write_text("__PLAYERS_JSON__|__CONFIG_JSON__", encoding="utf-8")
        rc = build_web.main([
            "--csv", str(csv_path), "--groups", str(groups_path),
            "--template", str(tpl_path), "--out", str(out_path),
        ])
        assert rc == 0
        html = out_path.read_text(encoding="utf-8")
        assert "梅西" in html and "position_groups" in html

    def test_missing_csv_returns_error(self, tmp_path, capsys):
        groups_path = tmp_path / "groups.json"
        tpl_path = tmp_path / "tpl.html"
        write_groups(groups_path)
        tpl_path.write_text("x", encoding="utf-8")
        rc = build_web.main([
            "--csv", str(tmp_path / "nope.csv"), "--groups", str(groups_path),
            "--template", str(tpl_path), "--out", str(tmp_path / "o.html"),
        ])
        assert rc != 0

    def test_script_entrypoint(self, tmp_path, monkeypatch):
        import runpy
        script = Path(build_web.__file__).resolve()
        csv_path = tmp_path / "players.csv"
        groups_path = tmp_path / "groups.json"
        tpl_path = tmp_path / "tpl.html"
        out_path = tmp_path / "index.html"
        write_csv(csv_path, [["梅西", "右边锋", "现役", "30", "迈阿密", "阿根廷", "170", "左"]])
        write_groups(groups_path)
        tpl_path.write_text("__PLAYERS_JSON__", encoding="utf-8")
        monkeypatch.setattr(sys, "argv", [
            str(script), "--csv", str(csv_path), "--groups", str(groups_path),
            "--template", str(tpl_path), "--out", str(out_path)])
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(script), run_name="__main__")
        assert exc.value.code == 0
        assert out_path.exists()
