"""Build a self-contained web/index.html from players.csv + groups.json.

Usage:
    python tools/build_web.py
    python tools/build_web.py --csv players.csv --groups groups.json \
        --template tools/web_template.html --out web/index.html
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

REQUIRED_FIELDS = ["球员", "位置", "类型", "背号", "俱乐部", "国籍", "身高", "惯用脚"]
REQUIRED_GROUP_KEYS = ["position_groups", "league_groups", "country_continent"]

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _norm_text(value):
    if value is None:
        return ""
    return re.sub(r"\s+", "", str(value))


def load_players(csv_path):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"未找到球员数据文件: {csv_path}")
    players = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            players.append({k: _norm_text(row.get(k)) for k in REQUIRED_FIELDS})
    return players


def load_groups(groups_path):
    groups_path = Path(groups_path)
    if not groups_path.exists():
        raise FileNotFoundError(f"未找到分组配置文件: {groups_path}")
    cfg = json.loads(groups_path.read_text(encoding="utf-8"))
    for key in REQUIRED_GROUP_KEYS:
        if key not in cfg:
            raise KeyError(f"groups.json 缺少必需字段: {key}")
    return cfg


def embed_json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def build_html(template, players, config):
    return (template
            .replace("__PLAYERS_JSON__", embed_json(players))
            .replace("__CONFIG_JSON__", embed_json(config)))


def main(argv=None):
    parser = argparse.ArgumentParser(description="生成单文件球员搜索网页")
    parser.add_argument("--csv", default=str(PROJECT_ROOT / "players.csv"))
    parser.add_argument("--groups", default=str(PROJECT_ROOT / "groups.json"))
    parser.add_argument("--template", default=str(PROJECT_ROOT / "tools" / "web_template.html"))
    parser.add_argument("--out", default=str(PROJECT_ROOT / "web" / "index.html"))
    args = parser.parse_args(argv)

    try:
        players = load_players(args.csv)
        config = load_groups(args.groups)
        template = Path(args.template).read_text(encoding="utf-8")
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"构建失败: {e}", file=sys.stderr)
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_html(template, players, config), encoding="utf-8")
    print(f"已生成 {out_path}（{len(players)} 名球员）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
