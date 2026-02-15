import csv
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox


POSITION_GROUPS = {
    "全部": [],
    "前场": ["中锋", "左边锋", "右边锋", "影锋"],
    "中场": ["前腰", "左前卫", "右前卫", "中前卫", "后腰"],
    "后场": ["左后卫", "右后卫", "中后卫", "门将"],
}


LEAGUE_GROUPS = {
    "全部": [],
    "英超": {
        "阿森纳",
        "阿斯顿维拉",
        "伯恩茅斯",
        "布莱顿",
        "布伦特福德",
        "富勒姆",
        "利物浦",
        "曼联",
        "曼城",
        "切尔西",
        "热刺",
        "水晶宫",
        "纽卡斯尔",
        "诺丁汉",
        "利兹联",
        "桑德兰",
        "埃弗顿",
        "沃尔弗汉普顿",
        "伯恩利"
    },
    "西甲": {
        "巴萨",
        "皇马",
        "马竞",
        "毕尔巴鄂",
        "比利亚雷亚尔",
        "塞维利亚特利亚纳",
        "塞维利亚内维翁",
        "巴斯科希普斯夸",
        "科莫",
        "毕尔巴鄂",
        "瓦伦西亚"
    },
    "意甲": {
        "AC米兰",
        "国米",
        "拉齐奥",
        "那不勒斯",
        "罗马",
        "佛罗伦萨",
        "尤文图斯",
        "亚特兰大",
        "拉齐奥",
        "那不勒斯",
        "博洛尼亚",
        "都灵",
        "热那亚"
    },
    "德甲": {
        "多特蒙德",
        "勒沃库森",
    },
    "法甲": {
        "摩纳哥",
        "哥特拉斯堡",
        "巴黎",
        "马赛",
        "里昂"
    },
    "葡超": {
        "葡萄牙体育",
        "本菲卡",
        "波尔图"
    },
    "荷甲": set(),
    "亚足联": {
        "利雅得胜利",
        "利雅得希拉尔",
        "吉达阿赫利"
    },
    "美职联": {
        "迈阿密",
        "洛杉矶"
    },
    "土超":{
        "贝西克塔斯",
        "费内巴切",
        "加拉塔萨雷",
        "贝西克塔斯"
    },
    "其他联赛":{
        "拜仁"
    }
}


COUNTRY_CONTINENT = {
    # 欧洲
    "英格兰": "欧洲",
    "法国": "欧洲",
    "德国": "欧洲",
    "意大利": "欧洲",
    "西班牙": "欧洲",
    "荷兰": "欧洲",
    "比利时": "欧洲",
    "葡萄牙": "欧洲",
    "挪威": "欧洲",
    "克罗地亚": "欧洲",
    "瑞士": "欧洲",
    "苏格兰": "欧洲",
    "威尔士": "欧洲",
    "斯洛伐克": "欧洲",
    # 南美
    "巴西": "南美洲",
    "阿根廷": "南美洲",
    "乌拉圭": "南美洲",
    "哥伦比亚": "南美洲",
    "厄瓜多尔": "南美洲",
    # 北美
    "美国": "北美洲",
    # 非洲
    "科特迪瓦": "非洲",
    "马里": "非洲",
    "加纳": "非洲",
    # 亚洲
    "日本": "亚洲",
    "卡塔尔": "亚洲",
    "中国": "亚洲",
}


class PlayerSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("球员搜索")
        self.players = []

        self.load_data()
        self.build_ui()
        # 绑定回车键为查询
        self.root.bind("<Return>", lambda event: self.on_search())

    def load_data(self):
        # 兼容 .py 运行和打包成 .exe 后运行：都从可执行文件所在目录读取 players.csv
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # PyInstaller onefile 场景，exe 所在目录
            base_dir = os.path.dirname(sys.executable)
        else:
            # 普通脚本运行
            base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, "players.csv")
        if not os.path.exists(csv_path):
            messagebox.showerror("错误", f"未找到 players.csv 文件: {csv_path}")
            self.root.destroy()
            return

        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["背号"] = row["背号"].strip() if row["背号"] is not None else ""
                row["身高"] = row["身高"].strip() if row["身高"] is not None else ""
                self.players.append(row)

        self.all_positions = sorted({p["位置"] for p in self.players if p.get("位置")})
        self.all_clubs = sorted({p["俱乐部"] for p in self.players if p.get("俱乐部")})
        self.all_countries = sorted({p["国籍"] for p in self.players if p.get("国籍")})
        self.all_feet = sorted({p["惯用脚"] for p in self.players if p.get("惯用脚")})

    def build_ui(self):
        filter_frame = ttk.LabelFrame(self.root, text="查询条件")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        row = 0

        ttk.Label(filter_frame, text="位置组别").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.position_group_var = tk.StringVar(value="全部")
        self.position_group_cb = ttk.Combobox(filter_frame, textvariable=self.position_group_var,
                                              values=list(POSITION_GROUPS.keys()), state="readonly", width=10)
        self.position_group_cb.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(filter_frame, text="排除组别").grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        self.position_exclude_group_var = tk.StringVar(value="全部")
        self.position_exclude_group_cb = ttk.Combobox(filter_frame, textvariable=self.position_exclude_group_var,
                                                      values=list(POSITION_GROUPS.keys()), state="readonly", width=10)
        self.position_exclude_group_cb.grid(row=row, column=3, sticky=tk.W, padx=5, pady=5)

        row += 1

        ttk.Label(filter_frame, text="精确位置").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.position_var = tk.StringVar()
        self.position_cb = ttk.Combobox(filter_frame, textvariable=self.position_var,
                                        values=self.all_positions, width=12)
        self.position_cb.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        row += 1

        ttk.Label(filter_frame, text="类型").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.type_var = tk.StringVar(value="全部")
        type_values = ["全部", "现役", "历史"]
        self.type_cb = ttk.Combobox(filter_frame, textvariable=self.type_var,
                                    values=type_values, state="readonly", width=12)
        self.type_cb.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        row += 1

        ttk.Label(filter_frame, text="背号范围").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.shirt_min_var = tk.StringVar()
        self.shirt_max_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.shirt_min_var, width=8).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(filter_frame, text="至").grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(filter_frame, textvariable=self.shirt_max_var, width=8).grid(row=row, column=3, sticky=tk.W, padx=5, pady=5)

        row += 1

        ttk.Label(filter_frame, text="俱乐部分组").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.league_group_var = tk.StringVar(value="全部")
        self.league_group_cb = ttk.Combobox(filter_frame, textvariable=self.league_group_var,
                                            values=list(LEAGUE_GROUPS.keys()), state="readonly", width=10)
        self.league_group_cb.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(filter_frame, text="排除分组").grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        self.league_exclude_group_var = tk.StringVar(value="全部")
        self.league_exclude_group_cb = ttk.Combobox(filter_frame, textvariable=self.league_exclude_group_var,
                                                    values=list(LEAGUE_GROUPS.keys()), state="readonly", width=10)
        self.league_exclude_group_cb.grid(row=row, column=3, sticky=tk.W, padx=5, pady=5)

        row += 1

        ttk.Label(filter_frame, text="精确俱乐部").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.club_var = tk.StringVar()
        self.club_cb = ttk.Combobox(filter_frame, textvariable=self.club_var,
                                    values=self.all_clubs, width=18)
        self.club_cb.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        row += 1

        ttk.Label(filter_frame, text="国籍大洲").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.continent_var = tk.StringVar(value="全部")
        continent_values = ["全部", "欧洲", "南美洲", "北美洲", "非洲", "亚洲", "大洋洲", "其他"]
        self.continent_cb = ttk.Combobox(filter_frame, textvariable=self.continent_var,
                                         values=continent_values, state="readonly", width=10)
        self.continent_cb.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(filter_frame, text="排除大洲").grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        self.continent_exclude_var = tk.StringVar(value="全部")
        self.continent_exclude_cb = ttk.Combobox(filter_frame, textvariable=self.continent_exclude_var,
                                                 values=continent_values, state="readonly", width=10)
        self.continent_exclude_cb.grid(row=row, column=3, sticky=tk.W, padx=5, pady=5)

        row += 1

        ttk.Label(filter_frame, text="精确国籍").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.country_var = tk.StringVar()
        self.country_cb = ttk.Combobox(filter_frame, textvariable=self.country_var,
                                       values=self.all_countries, width=12)
        self.country_cb.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        row += 1

        ttk.Label(filter_frame, text="身高范围(cm)").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.height_min_var = tk.StringVar()
        self.height_max_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.height_min_var, width=8).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(filter_frame, text="至").grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(filter_frame, textvariable=self.height_max_var, width=8).grid(row=row, column=3, sticky=tk.W, padx=5, pady=5)

        row += 1

        ttk.Label(filter_frame, text="惯用脚").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        feet_values = ["全部"] + self.all_feet
        self.foot_var = tk.StringVar(value="全部")
        self.foot_cb = ttk.Combobox(filter_frame, textvariable=self.foot_var,
                                    values=feet_values, state="readonly", width=12)
        self.foot_cb.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        row += 1

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=row, column=0, columnspan=4, sticky=tk.W, padx=5, pady=10)

        search_btn = ttk.Button(btn_frame, text="查询", command=self.on_search)
        search_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = ttk.Button(btn_frame, text="重置", command=self.on_reset)
        reset_btn.pack(side=tk.LEFT, padx=5)

        result_frame = ttk.LabelFrame(self.root, text="查询结果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columns = ["球员", "位置", "类型", "背号", "俱乐部", "国籍", "身高", "惯用脚"]
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            if col in ("球员", "俱乐部"):
                width = 140
            elif col == "国籍":
                width = 80
            else:
                width = 70
            self.tree.column(col, width=width, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(result_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)

        self.update_results(self.players)

    def parse_int(self, value):
        value = value.strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def get_continent(self, country):
        if not country:
            return "其他"
        return COUNTRY_CONTINENT.get(country, "其他")

    def on_search(self):
        filtered = self.players

        group = self.position_group_var.get()
        exclude_group = self.position_exclude_group_var.get()
        pos = self.position_var.get().strip()
        if group and group != "全部":
            group_positions = POSITION_GROUPS.get(group, [])
            filtered = [p for p in filtered if p.get("位置") in group_positions]
        if exclude_group and exclude_group != "全部":
            exclude_positions = POSITION_GROUPS.get(exclude_group, [])
            if exclude_positions:
                filtered = [p for p in filtered if p.get("位置") not in exclude_positions]
        if pos:
            filtered = [p for p in filtered if p.get("位置") == pos]

        player_type = self.type_var.get()
        if player_type and player_type != "全部":
            filtered = [p for p in filtered if p.get("类型") == player_type]

        min_shirt = self.parse_int(self.shirt_min_var.get())
        max_shirt = self.parse_int(self.shirt_max_var.get())
        if min_shirt is not None or max_shirt is not None:
            def shirt_ok(p):
                num = self.parse_int(p.get("背号", ""))
                if num is None:
                    return False
                if min_shirt is not None and num < min_shirt:
                    return False
                if max_shirt is not None and num > max_shirt:
                    return False
                return True

            filtered = [p for p in filtered if shirt_ok(p)]

        league_group = self.league_group_var.get()
        league_exclude_group = self.league_exclude_group_var.get()
        club = self.club_var.get().strip()
        if league_group and league_group != "全部":
            clubs_in_group = LEAGUE_GROUPS.get(league_group, set())
            filtered = [p for p in filtered if p.get("俱乐部") in clubs_in_group]
        if league_exclude_group and league_exclude_group != "全部":
            exclude_clubs = LEAGUE_GROUPS.get(league_exclude_group, set())
            if exclude_clubs:
                filtered = [p for p in filtered if p.get("俱乐部") not in exclude_clubs]
        if club:
            filtered = [p for p in filtered if p.get("俱乐部") == club]

        continent = self.continent_var.get()
        continent_exclude = self.continent_exclude_var.get()
        country = self.country_var.get().strip()
        if continent and continent != "全部":
            filtered = [p for p in filtered if self.get_continent(p.get("国籍")) == continent]
        if continent_exclude and continent_exclude != "全部":
            filtered = [p for p in filtered if self.get_continent(p.get("国籍")) != continent_exclude]
        if country:
            filtered = [p for p in filtered if p.get("国籍") == country]

        min_height = self.parse_int(self.height_min_var.get())
        max_height = self.parse_int(self.height_max_var.get())
        if min_height is not None or max_height is not None:
            def height_ok(p):
                h = self.parse_int(p.get("身高", ""))
                if h is None:
                    return False
                if min_height is not None and h < min_height:
                    return False
                if max_height is not None and h > max_height:
                    return False
                return True

            filtered = [p for p in filtered if height_ok(p)]

        foot = self.foot_var.get()
        if foot and foot != "全部":
            filtered = [p for p in filtered if p.get("惯用脚") == foot]

        self.update_results(filtered)

    def on_reset(self):
        self.position_group_var.set("全部")
        self.position_exclude_group_var.set("全部")
        self.position_var.set("")
        self.type_var.set("全部")
        self.shirt_min_var.set("")
        self.shirt_max_var.set("")
        self.league_group_var.set("全部")
        self.league_exclude_group_var.set("全部")
        self.club_var.set("")
        self.continent_var.set("全部")
        self.continent_exclude_var.set("全部")
        self.country_var.set("")
        self.height_min_var.set("")
        self.height_max_var.set("")
        self.foot_var.set("全部")
        self.update_results(self.players)

    def update_results(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in rows:
            values = [
                p.get("球员", ""),
                p.get("位置", ""),
                p.get("类型", ""),
                p.get("背号", ""),
                p.get("俱乐部", ""),
                p.get("国籍", ""),
                p.get("身高", ""),
                p.get("惯用脚", ""),
            ]
            self.tree.insert("", tk.END, values=values)


def main():
    root = tk.Tk()
    app = PlayerSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
