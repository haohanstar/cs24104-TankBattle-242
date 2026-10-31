# -*- coding: utf-8 -*-
"""生成实验一 EA 17.2 工程与 5 张图。

输出：
  model/TankBattle.qea
  report/assets/ea/fig2-1-wbs.png
  report/assets/ea/fig3-1-component.png
  report/assets/ea/fig3-2-usecase.png
  report/assets/ea/fig3-3-class.png
  report/assets/ea/fig3-4-activity.png
"""
import os
import traceback
from ea_helpers import ModelBuilder

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QEA = os.path.join(BASE, "model", "TankBattle.qea")
IMG = os.path.join(BASE, "model", "images", "raw")
LOG = os.path.join(BASE, "model", "build_ea.log")
os.makedirs(IMG, exist_ok=True)
logf = open(LOG, "w", encoding="utf-8")


def log(*a):
    print(*a, file=logf, flush=True)


def main():
    b = ModelBuilder(QEA, log=log, reset=True)
    try:
        try:
            b.rep.ActivateTechnology("Project")
            log("Project technology activated")
        except Exception as e:
            log("ActivateTechnology(Project) warning:", e)

        model = b.model
        plan = b.add_pkg(model, "01 项目计划", "plan", notes="实验一项目计划：WBS 与分工。")
        req = b.add_pkg(model, "02 需求", "req", notes="地图系统需求：参与者、用例。")
        design = b.add_pkg(model, "03 设计", "design", notes="地图系统设计：构件、类、活动。")

        # ---------------- WBS ----------------
        def task(key, name, notes=""):
            try:
                return b.add_elem(plan, key, "Task", stereotype="Task", display_name=name, notes=notes)
            except Exception as e:
                log("Task fallback:", key, e)
                return b.add_elem(plan, key, "Activity", stereotype="Task", display_name=name, notes=notes)

        root = task("WBS_ROOT", "坦克大战·联机复刻\n200 人时")
        phases = [
            ("W1", "1 项目计划\n18h"), ("W2", "2 需求分析\n28h"), ("W3", "3 系统设计\n34h"),
            ("W4", "4 编码实现\n84h"), ("W5", "5 测试与部署\n22h"), ("W6", "6 管理与答辩\n14h"),
        ]
        for k, n in phases:
            task(k, n)
        # 编码阶段的 L3
        l3 = [
            ("W41", "4.1 战斗引擎 14h\nA 姚于轩"), ("W42", "4.2 地图渲染 8h\nB 姚帅"),
            ("W43", "4.3 地图碰撞 8h\nB 姚帅"), ("W44", "4.4 编辑器+AI 16h\nB 姚帅"),
            ("W45", "4.5 房间服务 14h\nC 杨宇航"), ("W46", "4.6 道具升级 12h\nD 杨旭"),
            ("W47", "4.7 大厅战队 12h\nE 杨宁宁"),
        ]
        for k, n in l3:
            task(k, n)
        # B 模块 L4
        l4 = [
            ("W441", "4.4.1 Tiled 规范 4h"), ("W442", "4.4.2 校验 CLI 4h"),
            ("W443", "4.4.3 AI 生成 8h"),
        ]
        for k, n in l4:
            task(k, n)

        wd = b.add_diagram(plan, "项目 WBS（编码阶段与 B 模块展开）", "Custom",
                           notes="L1 项目 → L2 阶段 → L3 任务；编码阶段与 B 模块展开到 L4。完整 L3 见表 2-2。",
                           key="wbs")
        b.place(wd, root, 40, 50, 300, 70)
        phase_y = [150, 250, 350, 450, 550, 650]
        for (k, _), y in zip(phases, phase_y):
            b.place(wd, b.elements[k], 40, y, 300, 70)
        for i in range(len(phases)):
            b.connect(root, b.elements[phases[i][0]], "包含", "Aggregation")
        for i, (k, _) in enumerate(l3):
            y = 150 + i * 86
            e = b.elements[k]
            b.place(wd, e, 430, y, 260, 70)
            b.connect(b.elements["W4"], e, "分解", "Aggregation")
        for i, (k, _) in enumerate(l4):
            y = 408 + i * 78
            e = b.elements[k]
            b.place(wd, e, 790, y, 230, 64)
            b.connect(b.elements["W44"], e, "分解", "Aggregation")
        b.add_note(plan, wd,
                   "图例：矩形为 WBS 任务，括号内为估算工时与责任人。\n"
                   "L1 项目 → L2 阶段 → L3 任务包（4~16 人时）→ L4 关键任务子步骤。\n"
                   "其他阶段的 L3 任务见表 2-2；此处展开编码阶段和 B-地图系统，避免整图过宽。",
                   40, 850, 620, 130)
        b.style(wd, 9)
        b.set_scale(wd, 200)
        b.export(wd, os.path.join(IMG, "fig2-1-wbs.png"))

        # ---------------- 构件图 ----------------
        comps = [
            ("C_A", "A 战斗引擎\n移动/射击/碰撞", 40, 60, 210, 80),
            ("C_B", "B 地图系统\n渲染/碰撞/编辑器", 40, 200, 210, 80),
            ("C_D", "D 道具升级\n生成/拾取/升级", 40, 340, 210, 80),
            ("C_MAP", "«interface»\nMapService", 320, 200, 180, 70),
            ("C_SRV", "C 对战房间\nWebSocket/Netty", 580, 80, 230, 90),
            ("C_DB", "房间/排行数据\nPostgreSQL/Redis", 580, 230, 230, 80),
            ("C_E", "E 大厅战队\nVue3 H5", 580, 380, 230, 80),
            ("C_AI", "AI 地图服务\n难度参数/解释", 320, 380, 210, 80),
            ("C_TILED", "Tiled 1.12.2\n地图编辑端（输出 TMX）", 40, 500, 210, 70),
            ("C_CONTRACT", "地图契约\nmap_id/version/hash", 580, 520, 230, 70),
        ]
        for k, n, x, y, w, h in comps:
            b.add_elem(design, k, "Component", key=k, display_name=n)
        cd = b.add_diagram(design, "系统构件图", "Component",
                           notes="桌面端 A/B/D、Web 后端 C、移动端 E、地图契约与 AI 服务。",
                           key="component")
        for k, n, x, y, w, h in comps:
            b.place(cd, b.elements[k], x, y, w, h)
        b.connect("C_A", "C_MAP", "调用", "Dependency", direction="Source -> Destination")
        b.connect("C_B", "C_MAP", "实现", "Realization", direction="Source -> Destination")
        b.connect("C_D", "C_MAP", "查询空格", "Dependency", direction="Source -> Destination")
        b.connect("C_SRV", "C_MAP", "下发地图", "Dependency", direction="Source -> Destination")
        b.connect("C_SRV", "C_DB", "读写", "Dependency", direction="Source -> Destination")
        b.connect("C_E", "C_CONTRACT", "地图摘要", "Dependency", direction="Source -> Destination")
        b.connect("C_B", "C_AI", "生成/校验", "Dependency", direction="Source -> Destination")
        b.connect("C_SRV", "C_CONTRACT", "hash 校验", "Dependency", direction="Source -> Destination")
        b.add_note(design, cd,
                   "边界：A 负责坦克/子弹；B 只提供地形查询与地图数据；C 负责房间与状态同步；\n"
                   "D 用 freeCells() 放道具；E 只拿地图摘要/缩略图。Tiled 编辑端输出 TMX，由 B 加载。",
                   40, 620, 760, 80)
        b.style(cd, 9)
        b.set_scale(cd, 200)
        b.export(cd, os.path.join(IMG, "fig3-1-component.png"))

        # ---------------- 用例图 ----------------
        boundary = b.add_elem(req, "UC_BOUNDARY", "Boundary", key="UC_BOUNDARY",
                              display_name="坦克大战地图系统")
        actors = [("ACT_P", "玩家", 40, 120), ("ACT_E", "地图作者", 40, 420), ("ACT_AI", "AI 服务", 40, 720)]
        for k, n, x, y in actors:
            b.add_elem(req, k, "Actor", key=k, display_name=n)
        ucs = [
            ("U_LOAD", "加载地图", 320, 120, 180, 60),
            ("U_PREVIEW", "预览地图", 320, 220, 180, 60),
            ("U_SYNC", "同步地图", 320, 320, 180, 60),
            ("U_EDIT", "编辑地图", 600, 420, 180, 60),
            ("U_CHECK", "校验地图", 600, 520, 180, 60),
            ("U_INFO", "查看地图信息", 600, 620, 180, 60),
            ("U_GEN", "生成地图", 880, 720, 180, 60),
            ("U_DIFF", "选择难度", 880, 820, 180, 60),
        ]
        for k, n, x, y, w, h in ucs:
            b.add_elem(req, k, "UseCase", key=k, display_name=n)
        ud = b.add_diagram(req, "地图系统用例图", "Use Case",
                           notes="玩家、地图作者、AI 服务与地图系统的用例关系。",
                           key="usecase")
        b.place(ud, boundary, 260, 60, 840, 880)
        for k, n, x, y in actors:
            b.place(ud, b.elements[k], x, y, 160, 80)
        for k, n, x, y, w, h in ucs:
            b.place(ud, b.elements[k], x, y, w, h)
        b.connect("ACT_P", "U_LOAD", "", "Association")
        b.connect("ACT_P", "U_PREVIEW", "", "Association")
        b.connect("ACT_P", "U_SYNC", "", "Association")
        b.connect("ACT_E", "U_EDIT", "", "Association")
        b.connect("ACT_E", "U_CHECK", "", "Association")
        b.connect("ACT_E", "U_INFO", "", "Association")
        b.connect("ACT_AI", "U_GEN", "", "Association")
        b.connect("ACT_AI", "U_DIFF", "", "Association")
        b.connect("U_EDIT", "U_CHECK", "«include»", "UseCase", stereotype="include", direction="Source -> Destination")
        b.connect("U_PREVIEW", "U_LOAD", "«extend»", "UseCase", stereotype="extend", direction="Source -> Destination")
        b.add_note(req, ud,
                   "地图作者用 Tiled 编辑；游戏端只做加载/预览/校验。\n"
                   "AI 服务只给难度参数和校验解释，不直接输出瓦片；生成的图同样走校验。",
                   300, 980, 760, 70)
        b.style(ud, 9)
        b.set_scale(ud, 200)
        b.export(ud, os.path.join(IMG, "fig3-2-usecase.png"))

        # ---------------- 类图 ----------------
        classes = [
            ("CLS_MAP", "TileMap", 40, 40, 230, 140, [
                ("-width: Int", ""), ("-height: Int", ""), ("-tiles: List<Tile>", ""),
                ("+load(path): TileMap", ""), ("+isBlocked(rect): Bool", ""),
            ]),
            ("CLS_LAYER", "TileLayer", 310, 40, 210, 120, [
                ("-name: String", ""), ("-data: Int[]", ""), ("+at(cell): Tile", ""),
            ]),
            ("CLS_TILE", "Tile", 560, 40, 210, 140, [
                ("-type: TileType", ""), ("-hp: Int", ""), ("+isBlocked(): Bool", ""),
                ("+hit(power): BulletHit", ""),
            ]),
            ("CLS_TYPE", "TileType", 810, 40, 210, 170, [
                ("EMPTY / BRICK / STEEL", ""), ("WATER / ICE / GRASS / BASE", ""),
                ("+properties(): TerrainEffect", ""),
            ]),
            ("CLS_META", "MapMetadata", 40, 250, 230, 130, [
                ("mapId: String", ""), ("version: Int", ""), ("seed: Int", ""),
                ("difficulty: String", ""), ("hash: String", ""),
            ]),
            ("CLS_SVC", "MapService", 310, 250, 230, 160, [
                ("<<interface>>", ""), ("+load(id, ver)", ""), ("+isBlocked(rect, mover)", ""),
                ("+terrainAt(cell)", ""), ("+hitBullet(cell, power)", ""),
                ("+spawnPoints()", ""), ("+freeCells()", ""),
            ]),
            ("CLS_COL", "CollisionService", 580, 250, 230, 160, [
                ("+isBlocked(rect, mover)", ""), ("+terrainAt(cell)", ""),
                ("+resolveMove(rect, dx, dy)", ""),
            ]),
            ("CLS_REPO", "MapRepository", 850, 250, 210, 130, [
                ("+load(mapId, ver)", ""), ("+save(map)", ""), ("+hash(map)", ""),
            ]),
            ("CLS_VAL", "MapValidator", 310, 480, 230, 150, [
                ("+validate(map): Report", ""), ("+checkConnectivity()", ""),
                ("+checkBase()", ""), ("+checkRatios()", ""),
            ]),
            ("CLS_GEN", "MapGenerator", 580, 480, 230, 150, [
                ("+generate(diff, seed)", ""), ("+repair(map)", ""),
            ]),
            ("CLS_DIFF", "DifficultyProfile", 850, 480, 210, 130, [
                ("brickRatio: Float", ""), ("steelRatio: Float", ""),
                ("waterRatio: Float", ""), ("grassRatio: Float", ""),
            ]),
        ]
        for k, n, x, y, w, h, attrs in classes:
            e = b.add_elem(design, k, "Class", key=k, display_name=n)
            for an, at in attrs:
                b.add_attr(e, an, at or "")
        cl = b.add_diagram(design, "地图系统类图", "Logical",
                           notes="地图数据、服务接口、碰撞、校验与生成器的核心类。",
                           key="class")
        for k, n, x, y, w, h, attrs in classes:
            b.place(cl, b.elements[k], x, y, w, h)
        b.connect("CLS_MAP", "CLS_LAYER", "1..*", "Aggregation", subtype="Strong", client_card="1", supplier_card="1..*")
        b.connect("CLS_LAYER", "CLS_TILE", "1..*", "Aggregation", subtype="Strong", client_card="1", supplier_card="1..*")
        b.connect("CLS_TILE", "CLS_TYPE", "1", "Association", client_card="*", supplier_card="1")
        b.connect("CLS_SVC", "CLS_MAP", "加载", "Dependency", direction="Source -> Destination")
        b.connect("CLS_SVC", "CLS_META", "读取", "Dependency", direction="Source -> Destination")
        b.connect("CLS_COL", "CLS_SVC", "实现", "Realization")
        b.connect("CLS_REPO", "CLS_MAP", "存取", "Dependency", direction="Source -> Destination")
        b.connect("CLS_VAL", "CLS_MAP", "校验", "Dependency", direction="Source -> Destination")
        b.connect("CLS_GEN", "CLS_MAP", "生成", "Dependency", direction="Source -> Destination")
        b.connect("CLS_GEN", "CLS_DIFF", "参数", "Dependency", direction="Source -> Destination")
        b.add_note(design, cl,
                   "职责：A 只调用 MapService；B 内部由 CollisionService 做地形碰撞；\n"
                   "MapValidator 检查连通性/基地保护/地形比例；MapGenerator 只生成候选，不直接发布。",
                   40, 700, 980, 80)
        b.style(cl, 8)
        b.set_scale(cl, 200)
        b.export(cl, os.path.join(IMG, "fig3-3-class.png"))

        # ---------------- 活动图 ----------------
        acts = [
            ("A_START", "Initial", 80, 40, 30, 30, "StateNode", 100),
            ("A_CHOOSE", "选择难度/尺寸", 140, 100, 220, 60, "Action", None),
            ("A_EDIT", "Tiled 手工编辑", 140, 210, 220, 60, "Action", None),
            ("A_GEN", "生成候选地图", 450, 100, 220, 60, "Action", None),
            ("A_CHECK", "校验：连通/基地/比例", 760, 100, 240, 60, "Action", None),
            ("A_OK", "通过？", 900, 210, 90, 90, "Decision", None),
            ("A_SAVE", "保存/发布地图", 760, 350, 220, 60, "Action", None),
            ("A_REPAIR", "修复参数/重生成", 450, 350, 220, 60, "Action", None),
            ("A_LOAD", "加载到游戏", 760, 460, 220, 60, "Action", None),
            ("A_END", "Final", 850, 570, 30, 30, "StateNode", 101),
        ]
        for k, n, x, y, w, h, typ, sub in acts:
            b.add_elem(design, k, typ, key=k, display_name=n, subtype=sub)
        ad = b.add_diagram(design, "地图编辑与 AI 生成活动图", "Activity",
                           notes="手工编辑或 AI 生成 → 校验 → 通过/修复 → 保存 → 加载。",
                           key="activity")
        for k, n, x, y, w, h, typ, sub in acts:
            b.place(ad, b.elements[k], x, y, w, h)
        flows = [
            ("A_START", "A_CHOOSE", ""), ("A_CHOOSE", "A_GEN", ""),
            ("A_GEN", "A_CHECK", ""), ("A_CHECK", "A_OK", ""),
            ("A_OK", "A_SAVE", "[通过]"), ("A_OK", "A_REPAIR", "[不通过]"),
            ("A_REPAIR", "A_GEN", "重新生成"), ("A_SAVE", "A_LOAD", ""),
            ("A_LOAD", "A_END", ""), ("A_EDIT", "A_CHECK", "提交校验"),
        ]
        for s, t, g in flows:
            b.connect(s, t, g, "ControlFlow")
        b.add_note(design, ad,
                   "校验规则：出生点到基地连通、基地周围 ≥6 块砖、砖/钢/水/冰/草比例、出生点公平。\n"
                   "LLM 只负责难度参数与校验解释；生成失败时退回模板，不允许未校验地图发布。",
                   40, 640, 700, 80)
        b.style(ad, 9)
        b.set_scale(ad, 200)
        b.export(ad, os.path.join(IMG, "fig3-4-activity.png"))

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
