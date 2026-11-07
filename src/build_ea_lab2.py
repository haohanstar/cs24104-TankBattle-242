# -*- coding: utf-8 -*-
"""在 EA 17.2 中绘制实验二的 8 张图，并从工程导出 PNG。

输出：
  model/TankBattle.qea（在原实验一工程上追加“02 实验二 需求分析”包）
  model/images/lab2/raw/*.png           EA 原始导出（带试用版水印）
  docs/model/lab2/*.png                 去水印、白底黑线的交付图（由 clean_ea_images_lab2.py 生成）

用法：python src/build_ea_lab2.py
"""
import os
import shutil
import traceback
from ea_helpers import ModelBuilder

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QEA = os.path.join(BASE, "model", "TankBattle.qea")
RAW = os.path.join(BASE, "model", "images", "lab2", "raw")
LOG = os.path.join(BASE, "model", "build_ea_lab2.log")
os.makedirs(RAW, exist_ok=True)
logf = open(LOG, "w", encoding="utf-8")


def log(*a):
    print(*a, file=logf, flush=True)


def main():
    # 可重复运行：第一次运行时备份“只有实验一”的工程，之后每次都从备份恢复再追加
    bak = QEA + ".lab1bak"
    if os.path.exists(bak):
        shutil.copyfile(bak, QEA)
        log("restore from", bak)
    else:
        shutil.copyfile(QEA, bak)
        log("backup lab1 model ->", bak)

    # reset=False：保留实验一的模型，只在后面追加实验二的包
    b = ModelBuilder(QEA, log=log, reset=False)
    # 清空按名字缓存的字典，避免和实验一里的同名元素串到一起
    b.elements = {}
    b.packages = {}
    b.diagrams = {}
    try:
        model = b.model
        root = b.add_pkg(model, "02 实验二 需求分析", "L2", notes="实验二软件需求分析：DFD、用例、类图、顺序图。")
        p_dfd = b.add_pkg(root, "01 DFD", "L2_DFD")
        p_uc = b.add_pkg(root, "02 用例", "L2_UC")
        p_cls = b.add_pkg(root, "03 类图", "L2_CLS")
        p_seq = b.add_pkg(root, "04 顺序图", "L2_SEQ")

        # ---------- DFD 元素工厂 ----------
        def proc(pkg, key, text):
            # Activity（不挂 stereotype）：EA 里渲染为圆角矩形，符合 DFD 加工的规范画法
            return b.add_elem(pkg, key, "Activity", display_name=text, key=key)

        def ext(pkg, key, text):
            # Class 不挂成员时渲染为干净矩形（Object 会把名字加下划线，两行名会与下划线打架）
            return b.add_elem(pkg, key, "Class", stereotype="external entity", display_name=text, key=key)

        def store(pkg, key, text):
            return b.add_elem(pkg, key, "DataStore", display_name=text, key=key)

        def flow(diag, c, s, name):
            b.connect(c, s, name, "Association", direction="Source -> Destination")

        def bioflow(diag, c, s, name):
            b.connect(c, s, name, "Association", direction="Bi-Direction")

        # ================= 1. DFD 顶层 =================
        e_player = ext(p_dfd, "T_PLAYER", "玩家")
        e_spect = ext(p_dfd, "T_SPECT", "观战者")
        e_admin = ext(p_dfd, "T_ADMIN", "管理员")
        e_ai = ext(p_dfd, "T_AI", "AI 服务")
        p0 = proc(p_dfd, "T_SYS", "0\n坦克大战联机系统")

        d = b.add_diagram(p_dfd, "DFD-顶层", "Data Flow Diagram",
                          notes="顶层图：外部实体与系统之间的数据流，不画数据存储。", key="dfd_top")
        b.place(d, e_player, 40, 120, 170, 90)
        b.place(d, e_spect, 40, 380, 170, 90)
        b.place(d, e_admin, 40, 640, 170, 90)
        b.place(d, p0, 560, 230, 420, 400)
        b.place(d, e_ai, 1280, 380, 180, 90)

        flow(d, e_player, p0, "登录/房间操作/对战输入")
        flow(d, p0, e_player, "状态快照/结算")
        flow(d, e_spect, p0, "观战/回放请求")
        flow(d, p0, e_spect, "对局画面/回放数据")
        flow(d, e_admin, p0, "地图/用户管理")
        flow(d, p0, e_admin, "校验结果/管理报表")
        flow(d, p0, e_ai, "地图参数/解说请求/匹配请求")
        flow(d, e_ai, p0, "生成参数/解说文本/匹配结果")
        b.style(d, 11)
        b.set_scale(d, 200)
        b.export(d, os.path.join(RAW, "fig2-2-dfd-top.png"))

        # ================= 2. DFD 0 层 =================
        z_player = ext(p_dfd, "Z_PLAYER", "玩家")
        z_spect = ext(p_dfd, "Z_SPECT", "观战者")
        z_admin = ext(p_dfd, "Z_ADMIN", "管理员")
        z_ai = ext(p_dfd, "Z_AI", "AI 服务")
        p1 = proc(p_dfd, "Z_P1", "P1\n登录与大厅")
        p2 = proc(p_dfd, "Z_P2", "P2\n房间匹配")
        p3 = proc(p_dfd, "Z_P3", "P3\n战斗引擎")
        p4 = proc(p_dfd, "Z_P4", "P4\n地图服务")
        p5 = proc(p_dfd, "Z_P5", "P5\n道具升级")
        p6 = proc(p_dfd, "Z_P6", "P6\n排行/锦标赛")
        d1 = store(p_dfd, "Z_D1", "D1 用户库")
        d2 = store(p_dfd, "Z_D2", "D2 房间库")
        d3 = store(p_dfd, "Z_D3", "D3 对局库")
        d4 = store(p_dfd, "Z_D4", "D4 地图库")
        d5 = store(p_dfd, "Z_D5", "D5 道具配置")
        d6 = store(p_dfd, "Z_D6", "D6 排行榜")

        d = b.add_diagram(p_dfd, "DFD-0层", "Data Flow Diagram",
                          notes="0 层图：P1~P6 六个加工与 D1~D6 六个数据存储。", key="dfd0")
        b.place(d, z_spect, 20, 20, 210, 80)
        b.place(d, z_player, 20, 300, 190, 210)
        b.place(d, z_admin, 20, 640, 190, 90)
        b.place(d, z_ai, 20, 900, 190, 90)
        b.place(d, p1, 340, 60, 220, 90)
        b.place(d, p2, 340, 180, 220, 90)
        b.place(d, p3, 340, 300, 220, 90)
        b.place(d, p6, 620, 780, 220, 90)
        b.place(d, p4, 620, 440, 220, 90)
        b.place(d, p5, 620, 620, 220, 90)
        b.place(d, d1, 1060, 75, 190, 60)
        b.place(d, d2, 1060, 195, 190, 60)
        b.place(d, d3, 1060, 315, 190, 60)
        b.place(d, d4, 1060, 455, 190, 60)
        b.place(d, d5, 1060, 615, 190, 60)
        b.place(d, d6, 1060, 735, 190, 60)

        bioflow(d, z_player, p1, "登录账号/token+角色")
        flow(d, p1, d1, "读写用户")
        bioflow(d, z_player, p2, "房间条件/房间号+队伍")
        flow(d, p2, d2, "读写房间")
        flow(d, p2, p3, "开局")
        flow(d, p3, d3, "写对局")
        bioflow(d, p3, p4, "地形查询/命中结果")
        flow(d, p4, d4, "读地图")
        bioflow(d, p3, p5, "拾取结算/属性变化")
        flow(d, p5, d5, "读道具配置")
        flow(d, p3, p6, "对局结果")
        flow(d, p6, d6, "写排行")
        flow(d, p6, z_player, "积分/排名")
        bioflow(d, z_spect, p3, "观战请求/状态流")
        bioflow(d, z_admin, p4, "地图管理/校验结果")
        bioflow(d, p3, z_ai, "解说请求/解说文本")
        b.style(d, 10)
        b.set_scale(d, 200)
        b.export(d, os.path.join(RAW, "fig2-3-dfd-0.png"))

        # ================= 3. DFD 1 层：P3 战斗引擎 =================
        f_player = ext(p_dfd, "F_PLAYER", "玩家")
        f_p4 = ext(p_dfd, "F_P4", "P4 地图服务\n（跨图引用）")
        f_p5 = ext(p_dfd, "F_P5", "P5 道具升级\n（跨图引用）")
        f_c = ext(p_dfd, "F_C", "C 房间服务\n（跨图引用）")
        q1 = proc(p_dfd, "F_P31", "P3.1\n输入处理")
        q2 = proc(p_dfd, "F_P32", "P3.2\n移动与地形碰撞")
        q3 = proc(p_dfd, "F_P33", "P3.3\n射击与弹道")
        q4 = proc(p_dfd, "F_P34", "P3.4\n伤害/死亡/复活")
        q5 = proc(p_dfd, "F_P35", "P3.5\n状态广播")
        fd3 = store(p_dfd, "F_D3", "D3 对局库")
        fd5 = store(p_dfd, "F_D5", "D5 道具配置")

        d = b.add_diagram(p_dfd, "DFD-1层-战斗", "Data Flow Diagram",
                          notes="P3 战斗引擎展开为 P3.1~P3.5；跨图引用用方框标注去向。", key="dfd1_battle")
        b.place(d, f_player, 20, 80, 170, 90)
        b.place(d, q1, 280, 60, 200, 90)
        b.place(d, q2, 560, 60, 230, 90)
        b.place(d, q3, 560, 190, 230, 90)
        b.place(d, f_c, 880, 60, 190, 90)
        b.place(d, q5, 880, 190, 190, 90)
        b.place(d, q4, 560, 330, 230, 90)
        b.place(d, fd3, 880, 350, 180, 60)
        b.place(d, f_p4, 30, 260, 200, 90)
        b.place(d, f_p5, 30, 500, 200, 90)
        b.place(d, fd5, 30, 640, 180, 60)

        flow(d, f_player, q1, "按键/触屏")
        flow(d, q1, q2, "移动指令")
        flow(d, q2, f_p4, "isBlocked/terrainAt")
        flow(d, f_p4, q2, "可走/阻挡")
        flow(d, q1, q3, "射击指令")
        flow(d, q3, f_p4, "hitBullet(cell, power)")
        flow(d, q3, q4, "命中/伤害")
        flow(d, q4, q5, "死亡/复活事件")
        flow(d, q5, f_c, "STATE_SNAPSHOT")
        flow(d, q4, fd3, "写对局事件")
        flow(d, f_p5, q4, "道具效果")
        flow(d, fd5, f_p5, "道具配置")
        b.style(d, 10)
        b.set_scale(d, 200)
        b.export(d, os.path.join(RAW, "fig2-4-dfd-1-battle.png"))

        # ================= 4. DFD 1 层：P4 地图服务 =================
        g_c = ext(p_dfd, "G_C", "C 房间服务 / 客户端\n（跨图引用）")
        g_a = ext(p_dfd, "G_A", "A 战斗引擎\n（跨图引用）")
        r1 = proc(p_dfd, "G_P41", "P4.1\n地图加载")
        r2 = proc(p_dfd, "G_P42", "P4.2\n地形查询")
        r3 = proc(p_dfd, "G_P43", "P4.3\n子弹命中")
        r4 = proc(p_dfd, "G_P44", "P4.4\n出生点/空位")
        gd4 = store(p_dfd, "G_D4", "D4 地图库")
        gd3 = store(p_dfd, "G_D3", "D3 对局库")

        d = b.add_diagram(p_dfd, "DFD-1层-地图", "Data Flow Diagram",
                          notes="P4 地图服务展开为 P4.1~P4.4。", key="dfd1_map")
        b.place(d, g_c, 40, 60, 200, 90)
        b.place(d, gd4, 40, 270, 200, 70)
        b.place(d, r4, 40, 430, 200, 90)
        b.place(d, r1, 300, 60, 250, 90)
        b.place(d, r2, 620, 60, 220, 90)
        b.place(d, g_a, 620, 300, 200, 90)
        b.place(d, r3, 620, 470, 230, 90)
        b.place(d, gd3, 940, 480, 180, 60)

        flow(d, g_c, r1, "map_id/version")
        flow(d, r1, gd4, "读地图数据")
        flow(d, r1, r2, "TileMap")
        flow(d, r2, g_a, "isBlocked/terrainAt")
        flow(d, g_a, r3, "hitBullet(cell, power)")
        flow(d, r3, g_c, "TileDestroyed")
        flow(d, r3, gd3, "写破坏事件")
        flow(d, r4, g_a, "出生点/空位")
        flow(d, r4, gd4, "读地图元数据")
        b.style(d, 10)
        b.set_scale(d, 200)
        b.export(d, os.path.join(RAW, "fig2-4b-dfd-1-map.png"))

        # ================= 5. 用例图 =================
        b.add_elem(p_uc, "UC_BOUND", "Boundary", key="UC_BOUND", display_name="坦克大战联机系统")
        actors = [(("UC_A_P", "玩家"), 60, 400), (("UC_A_S", "观战者"), 1480, 120),
                  (("UC_A_M", "管理员"), 1480, 700), (("UC_A_AI", "AI 服务"), 740, 1030)]
        for (k, n), x, y in actors:
            b.add_elem(p_uc, k, "Actor", key=k, display_name=n)

        ucs = [
            ("UC01", "UC-01\n登录与鉴权", 760, 400, 200, 80),
            ("UC02", "UC-02\n创建/加入房间", 370, 40, 200, 70),
            ("UC03", "UC-03\n准备/开始对战", 370, 150, 200, 70),
            ("UC04", "UC-04\n移动/射击/用武器", 370, 260, 200, 70),
            ("UC05", "UC-05\n拾取/使用道具", 370, 370, 200, 70),
            ("UC06", "UC-06\n升级坦克", 370, 480, 200, 70),
            ("UC07", "UC-07\n观战", 1120, 120, 200, 70),
            ("UC08", "UC-08\n录像回放/AI 解说", 1120, 230, 200, 70),
            ("UC09", "UC-09\n地图选择/加载", 370, 590, 200, 70),
            ("UC10", "UC-10\n地图编辑/校验", 1120, 620, 200, 70),
            ("UC11", "UC-11\n好友/组队/战队", 370, 700, 200, 70),
            ("UC12", "UC-12\n排行榜/锦标赛", 370, 810, 200, 70),
            ("UC13", "UC-13\n后台管理", 1120, 730, 200, 70),
        ]
        for k, n, x, y, w, h in ucs:
            b.add_elem(p_uc, k, "UseCase", key=k, display_name=n)

        d = b.add_diagram(p_uc, "用例图", "Use Case",
                          notes="13 个用例；include 箭头由基础用例指向 UC-01，extend 由扩展用例指向基础用例。", key="usecase")
        b.place(d, b.elements["UC_BOUND"], 280, 20, 1120, 1000)
        for (k, n), x, y in actors:
            b.place(d, b.elements[k], x, y, 110, 100)
        for k, n, x, y, w, h in ucs:
            b.place(d, b.elements[k], x, y, w, h)

        # 参与者关联
        for k in ["UC02", "UC03", "UC04", "UC05", "UC06", "UC09", "UC11", "UC12"]:
            b.connect("UC_A_P", k, "", "Association")
        b.connect("UC_A_S", "UC07", "", "Association")
        b.connect("UC_A_S", "UC08", "", "Association")
        b.connect("UC_A_M", "UC10", "", "Association")
        b.connect("UC_A_M", "UC13", "", "Association")
        b.connect("UC_A_AI", "UC04", "", "Association")
        b.connect("UC_A_AI", "UC08", "", "Association")
        b.connect("UC_A_AI", "UC10", "", "Association")

        # include：基础用例 -> UC-01
        for k in ["UC02", "UC03", "UC04", "UC05", "UC06", "UC07", "UC08", "UC09", "UC10", "UC11", "UC12", "UC13"]:
            b.connect(k, "UC01", "", "UseCase", stereotype="include", direction="Source -> Destination")
        # extend：扩展用例 -> 基础用例
        b.connect("UC08", "UC07", "", "UseCase", stereotype="extend", direction="Source -> Destination")
        b.connect("UC06", "UC05", "", "UseCase", stereotype="extend", direction="Source -> Destination")
        b.style(d, 10)
        b.set_scale(d, 200)
        b.export(d, os.path.join(RAW, "fig2-5-usecase.png"))

        # ================= 6. 类图 =================
        cls_def = [
            ("C_USER", "User", "Class", 40, 40, [
                ("account: String", ""), ("passwordHash: String", ""), ("role: String", ""),
                ("login(account: String, password: String): Token", ""), ("logout(): void", ""),
            ]),
            ("C_PLAYER", "Player", "Class", 300, 40, [
                ("nickname: String", ""), ("teamId: String", ""), ("status: String", ""),
                ("joinRoom(roomId: String): void", ""), ("leaveRoom(): void", ""),
            ]),
            ("C_TANK", "Tank", "Class", 560, 40, [
                ("playerId: String", ""), ("x: int", ""), ("y: int", ""), ("dir: int", ""),
                ("hp: int", ""), ("speed: float", ""),
                ("move(dx: float, dy: float): void", ""), ("turn(dir: int): void", ""), ("hit(power: int): void", ""),
            ]),
            ("C_BULLET", "Bullet", "Class", 820, 40, [
                ("ownerId: String", ""), ("type: String", ""), ("x: int", ""), ("y: int", ""),
                ("power: int", ""), ("update(dt: float): void", ""), ("hit(target: Object): void", ""),
            ]),
            ("C_WEAPON", "Weapon", "Class", 1080, 40, [
                ("type: String", ""), ("damage: int", ""), ("cooldown: int", ""), ("ammo: int", ""),
                ("fire(owner: Tank): Bullet", ""), ("reload(): void", ""),
            ]),
            ("C_ROOM", "Room", "Class", 40, 290, [
                ("roomId: String", ""), ("mapId: String", ""), ("state: String", ""),
                ("maxPlayers: int", ""), ("join(playerId: String): void", ""),
                ("leave(playerId: String): void", ""), ("start(): void", ""),
            ]),
            ("C_MATCH", "Match", "Class", 300, 290, [
                ("matchId: String", ""), ("roomId: String", ""), ("startedAt: DateTime", ""),
                ("winner: String", ""), ("start(): void", ""), ("finish(): void", ""),
            ]),
            ("C_MAP", "Map", "Class", 560, 290, [
                ("mapId: String", ""), ("version: int", ""), ("hash: String", ""),
                ("size: Size", ""), ("load(id: String, ver: int): TileMap", ""), ("metadata(): MapMetadata", ""),
            ]),
            ("C_TILE", "Tile", "Class", 820, 290, [
                ("x: int", ""), ("y: int", ""), ("type: String", ""), ("hp: int", ""),
                ("destructible: bool", ""), ("isBlocked(): bool", ""), ("hit(power: int): BulletHit", ""),
            ]),
            ("C_ITEM", "Item", "Class", 1080, 290, [
                ("itemId: String", ""), ("type: String", ""), ("x: int", ""), ("y: int", ""),
                ("effect: String", ""), ("spawn(cell: Cell): void", ""), ("pickup(playerId: String): void", ""),
            ]),
            ("C_UPGRADE", "Upgrade", "Class", 40, 540, [
                ("upgradeId: String", ""), ("level: int", ""), ("cost: int", ""),
                ("effect: String", ""), ("apply(tank: Tank): void", ""),
            ]),
            ("C_TEAM", "Team", "Class", 300, 540, [
                ("teamId: String", ""), ("name: String", ""), ("ownerId: String", ""),
                ("addMember(playerId: String): void", ""), ("removeMember(playerId: String): void", ""),
            ]),
            ("C_RANK", "Ranking", "Class", 560, 540, [
                ("seasonId: String", ""), ("playerId: String", ""), ("score: int", ""),
                ("winRate: float", ""), ("update(result: MatchResult): void", ""), ("query(topN: int): List", ""),
            ]),
            ("C_REPLAY", "Replay", "Class", 820, 540, [
                ("replayId: String", ""), ("matchId: String", ""), ("events: List", ""),
                ("save(): void", ""), ("load(): List", ""),
            ]),
            ("C_AICOMM", "AICommentary", "Class", 1080, 540, [
                ("matchId: String", ""), ("text: String", ""), ("model: String", ""),
                ("generate(): String", ""),
            ]),
            ("C_MAPSVC", "MapService", "Interface", 560, 760, [
                ("load(id: String, ver: int): TileMap", ""), ("isBlocked(rect: Rect, mover: String): bool", ""),
                ("terrainAt(cell: Cell): TerrainEffect", ""), ("hitBullet(cell: Cell, power: int): BulletHit", ""),
                ("spawnPoints(): List", ""), ("freeCells(): List", ""), ("metadata(): MapMetadata", ""),
            ]),
        ]
        for k, n, typ, x, y, members in cls_def:
            e = b.add_elem(p_cls, k, typ, key=k, display_name=n)
            for m, t in members:
                if "(" in m:
                    pname = m.split("(")[0].replace("+", "").replace("-", "").strip()
                    ret = m.split("):")[-1].strip() if "):" in m else "void"
                    params = []
                    raw = m[m.index("(") + 1:m.index(")")]
                    if raw.strip():
                        for piece in raw.split(","):
                            pn, _, pt = piece.partition(":")
                            params.append((pn.strip(), pt.strip() or "Object"))
                    b.add_method(e, pname, ret or "void", params=params)
                elif ": " in m:
                    an, at = m.split(": ", 1)
                    b.add_attr(e, an.strip(), at.strip())

        d = b.add_diagram(p_cls, "类图", "Logical",
                          notes="15 个领域类 + MapService 接口；组合关系菱形在整体一端。", key="class")
        for k, n, typ, x, y, members in cls_def:
            h = 55 + 17 * len(members)
            if typ == "Interface":
                h = 75 + 17 * len(members)
            b.place(d, b.elements[k], x, y, 230, h)

        b.connect("C_TANK", "C_BULLET", "", "Association", client_card="1", supplier_card="0..*")
        b.connect("C_PLAYER", "C_TANK", "", "Aggregation", subtype="Strong", client_card="1", supplier_card="1")
        b.connect("C_ROOM", "C_MATCH", "", "Association", client_card="1", supplier_card="0..1")
        b.connect("C_MATCH", "C_REPLAY", "", "Aggregation", subtype="Strong", client_card="1", supplier_card="0..1")
        b.connect("C_MAP", "C_TILE", "", "Aggregation", subtype="Strong", client_card="1", supplier_card="1..*")
        b.connect("C_TEAM", "C_PLAYER", "", "Association", client_card="1", supplier_card="0..*")
        b.connect("C_PLAYER", "C_RANK", "", "Association", client_card="1", supplier_card="0..*")
        b.connect("C_MATCH", "C_AICOMM", "", "Association", client_card="1", supplier_card="0..1")
        b.connect("C_USER", "C_PLAYER", "", "Association", client_card="1", supplier_card="0..1")
        b.connect("C_MAP", "C_MAPSVC", "实现", "Realization", direction="Source -> Destination")
        b.style(d, 9)
        b.set_scale(d, 200)
        b.export(d, os.path.join(RAW, "fig2-6-class.png"))

        # ================= 7. 顺序图：房间加入 =================
        def lifeline(pkg, key, name, x, diag, y=90, w=170, h=70):
            e = b.add_elem(pkg, key, "Object", key=key, display_name=name)
            b.place(diag, e, x, y, w, h)
            return e

        sq1 = b.add_diagram(p_seq, "顺序图-房间加入", "Sequence",
                            notes="加入房间、准备、开局到初始状态同步。", key="seq_room")
        l_player = lifeline(p_seq, "SQ_P", "玩家", 100, sq1, w=120)
        l_client = lifeline(p_seq, "SQ_C", "客户端", 340, sq1, w=140)
        l_srv = lifeline(p_seq, "SQ_S", "C 房间服务", 660, sq1, w=160)
        l_db = lifeline(p_seq, "SQ_D", "房间库", 980, sq1, w=140)

        msgs = [(l_player, l_client, "1 JOIN_ROOM(roomId)"),
                (l_client, l_srv, "2 joinRoom(roomId, userId)"),
                (l_srv, l_db, "3 校验房间状态(roomId)"),
                (l_db, l_srv, "4 getRoomInfo(roomId)"),
                (l_srv, l_client, "5 ROOM_STATE(state)"),
                (l_client, l_srv, "6 READY(playerId)"),
                (l_srv, l_srv, "7 allReady()"),
                (l_srv, l_client, "8 START(matchId)"),
                (l_srv, l_client, "9 STATE_SNAPSHOT(tick, entities)")]
        for i, (c, s, txt) in enumerate(msgs, start=1):
            b.connect(c, s, txt, "Sequence", direction="Source -> Destination", seq_no=i)
        b.style(sq1, 9)
        b.set_scale(sq1, 200)
        b.export(sq1, os.path.join(RAW, "fig2-7-sequence-room.png"))

        # ================= 8. 顺序图：战斗射击 =================
        sq2 = b.add_diagram(p_seq, "顺序图-战斗射击", "Sequence",
                            notes="输入、移动、射击、地形查询与状态广播。", key="seq_battle")
        m_player = lifeline(p_seq, "SB_P", "玩家", 100, sq2, w=120)
        m_client = lifeline(p_seq, "SB_C", "客户端", 300, sq2, w=140)
        m_engine = lifeline(p_seq, "SB_E", "A 战斗引擎", 540, sq2, w=150)
        m_map = lifeline(p_seq, "SB_M", "B 地图服务", 800, sq2, w=150)
        m_room = lifeline(p_seq, "SB_R", "C 房间服务", 1060, sq2, w=150)

        msgs2 = [(m_client, m_engine, "1 PLAYER_INPUT(tick)"), (m_engine, m_engine, "2 move(dx, dy)"),
                 (m_engine, m_map, "3 isBlocked(rect, mover)"), (m_map, m_engine, "4 碰撞结果(可走/阻挡)"),
                 (m_client, m_engine, "5 SHOOT(dir)"), (m_engine, m_engine, "6 生成子弹(武器参数)"),
                 (m_engine, m_map, "7 hitBullet(cell, power)"), (m_map, m_room, "8 TileDestroyed(cell)"),
                 (m_engine, m_engine, "9 命中坦克(扣血)"), (m_engine, m_room, "10 STATE_SNAPSHOT(tick)"),
                 (m_room, m_client, "11 MAP_STATE(cell, type)"), (m_room, m_client, "12 STATE_SNAPSHOT(tick)")]
        for i, (c, s, txt) in enumerate(msgs2, start=1):
            b.connect(c, s, txt, "Sequence", direction="Source -> Destination", seq_no=i)
        b.style(sq2, 9)
        b.set_scale(sq2, 200)
        b.export(sq2, os.path.join(RAW, "fig2-7b-sequence-battle.png"))

        b.save()
        log("ALL OK")
    except Exception:
        log("ERROR")
        log(traceback.format_exc())
        raise
    finally:
        try:
            b.close()
        except Exception as e:
            log("close warning:", e)
        logf.close()


if __name__ == "__main__":
    main()
