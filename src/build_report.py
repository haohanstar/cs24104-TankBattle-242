# -*- coding: utf-8 -*-
"""生成实验一报告 DOCX。"""
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import report_helpers as R

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE, "report", "assets")
OUT = os.path.join(BASE, "report", "坦克大战实验一报告.docx")


def para(doc, text, **kw):
    return R.body(doc, text, **kw)


def cover(doc):
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("软件工程基础（2024 版）")
    R.set_run_font(r, R.BODY_FONT, 14, color=R.HEADER_COLOR)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("实验一　软件项目计划")
    R.set_run_font(r, R.HEAD_FONT, 26, bold=True, color=R.ACCENT)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("坦克大战·联机复刻")
    R.set_run_font(r, R.HEAD_FONT, 15, bold=True, color=R.HEADER_COLOR)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("第一阶段（初稿）")
    R.set_run_font(r, R.BODY_FONT, 11, color=R.HEADER_COLOR)

    doc.add_paragraph()
    rows = [
        ("课程名称", "软件工程基础（2024 版）", "实验名称", "实验一 软件项目计划"),
        ("组别", "cs24104", "班级", "计科 242"),
        ("学号", "2024210622", "姓名", "姚帅"),
        ("角色", "组长 · B-地图系统（桌面端）", "版本", "第一阶段（初稿）"),
        ("实验项目", "坦克大战·联机复刻（cs24104）", "应用端", "桌面端 + Web 后端 + H5"),
        ("日期", "2026-10-31", "仓库", "本地 Git 已建，待上传 GitHub"),
    ]
    table = doc.add_table(rows=0, cols=4)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            R.set_run_font(r, R.BODY_FONT, 9.5, bold=(i % 2 == 0))
    R.set_col_widths(table, [2.8, 5.6, 2.8, 5.6])

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("本报告为实验一初稿：本阶段完成项目计划、仓库基线、EA 模型和地图模块设计；\n游戏代码从实验四开始，不在本阶段塞半成品。")
    R.set_run_font(r, R.BODY_FONT, 9, color=R.HEADER_COLOR)


def toc(doc):
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("目　录")
    R.set_run_font(r, R.HEAD_FONT, 18, bold=True, color=R.ACCENT)
    R.add_toc(doc)


def two_images(doc, p1, p2, width_cm, cap):
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for i, path in enumerate((p1, p2)):
        cell = table.cell(0, i)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        p.add_run().add_picture(path, width=Cm(width_cm))
        cell.width = Cm(width_cm + 0.2)
        cell.vertical_alignment = 1
    R.caption(doc, cap, "图")


def chapter1(doc):
    R.h(doc, "一、项目与团队", 1, page_break=True)
    para(doc, "实验一不写游戏代码，重点是把 5 个人、8 周、3 类应用端拆成能指派、能验收的任务。下面先交代项目和分工，再给出 WBS、进度、风险和我的地图模块设计。")

    R.h(doc, "1.1 实验任务与交付", 2)
    para(doc, "老师的要求是完成实验一软件项目计划的初稿：小组统一名称、协作任务分工、建模用 EA、补齐个人任务和空项，最后提交 PDF 和源码 zip。本阶段交付计划、仓库基线、EA 模型和地图模块设计；游戏代码从实验四开始。")
    R.add_table(doc, ["交付物", "形态", "验收口径"], [
        ("实验一报告", "PDF，A4 竖版，目录页码", "5 张 EA 图 + 甘特/风险图；版式统一、图表编号连续"),
        ("本地 Git 仓库", "main/develop/feature，4 次提交", "README 能照着 push GitHub"),
        ("EA 工程", "model/TankBattle.qea", "5 张图能打开、能导出，中文正常"),
        ("地图规范", "docs/map-spec.md", "图层/属性/API/校验规则齐全"),
        ("AI 记录", "docs/ai-log.md", "6 条 Prompt/输出/处理/结论"),
        ("源码 zip", "报告源/EA/图/脚本/文档", "审完后由组长打包；不含第三方库"),
        ("游戏代码", "W13 起进入仓库", "实验一不塞半成品"),
    ], [3.4, 6.0, 7.4], 8, caption_text="表 1-1　实验一交付物与验收口径")

    R.h(doc, "1.2 项目概况", 2)
    para(doc, "项目是经典《坦克大战》的联机复刻：保留砖墙、钢墙、水域、冰面、草丛和基地，加入地图编辑、AI 地图生成、道具升级、房间观战和大厅战队。5 个人覆盖桌面端、Web 后端和移动端 H5，目标是在第 17 周做出能联机演示的版本。")
    R.add_table(doc, ["项目要素", "内容"], [
        ("项目名称", "坦克大战·联机复刻"),
        ("仓库", "cs24104-TankBattle"),
        ("方向 / 难度", "网游方向 / ★★★★"),
        ("应用端", "桌面端 + Web 后端 + 移动端 H5"),
        ("桌面端", "Kotlin 2.4.21 + JDK 21 + Gradle 9.8.1 + LibGDX + Tiled 1.12.2"),
        ("工具", "Python 3.12（离线生成/校验）、Git、EA 17.2、IDEA CE"),
        ("服务端", "Spring Boot + WebSocket + Netty"),
        ("H5", "Vue3 + WebSocket + ECharts"),
        ("周期", "第 10~17 教学周，5 人"),
    ], [4.0, 12.8], 8, caption_text="表 1-2　项目概况")

    R.h(doc, "1.3 团队分工", 2)
    para(doc, "5 个人每人 3 项功能，共 15 项；应用端去重后是桌面端 3 人、Web 后端 1 人、H5 1 人，覆盖 3 类。B 和 A 的边界最容易混：A 负责坦克-坦克、坦克-子弹、武器与弹道；我只负责坦克/子弹-地形，通过 MapService 查询，不在 B 里再写一套碰撞。")
    R.add_table(doc, ["姓名", "角色", "应用端", "3 项功能", "特色/AI", "备份"], [
        ("姚帅（组长）", "B-地图系统", "桌面端", "多地形渲染、地图编辑器、地形碰撞", "AI 地图生成", "姚于轩"),
        ("姚于轩", "A-战斗引擎", "桌面端", "移动/转向、射击/弹道、碰撞/武器", "AI 智能瞄准", "杨旭"),
        ("杨宇航", "C-对战房间", "Web 后端", "房间管理、状态同步、观战/回放", "AI 解说", "杨宁宁"),
        ("杨旭", "D-道具升级", "桌面端", "道具生成、拾取/效果、升级树", "AI 道具投放", "姚于轩"),
        ("杨宁宁", "E-大厅战队", "H5", "登录/好友、组队/战队、排行榜/锦标赛", "AI 匹配", "杨宇航"),
    ], [2.4, 2.3, 2.0, 5.4, 2.7, 2.0], 7.5, caption_text="表 1-3　团队成员与角色分工")

    R.h(doc, "1.4 我的角色与接口", 2)
    para(doc, "我既是组长，也是 B-地图系统的责任人：管理线负责仓库、WBS、计划统稿、评审组织；技术线负责地图渲染、碰撞、编辑器和 AI 生成。两项合计 48 人时（B 42 + 管理 6），比组内平均值高，但都在 WBS 里写清楚，不靠“组长多干点”含糊过去。")
    R.add_table(doc, ["对方", "他负责", "我提供", "我依赖他", "约定"], [
        ("A 战斗引擎", "坦克/子弹/武器", "isBlocked、terrainAt、hitBullet、出生点", "战斗循环调用我的接口", "W11 冻结签名"),
        ("C 对战房间", "房间/同步/观战", "map_id/version/hash、MAP_STATE 事件", "下发地图元数据", "W12 定协议"),
        ("D 道具升级", "道具生成/拾取", "freeCells()、道具候选点", "道具不改变地形", "W12 定规则"),
        ("E 大厅战队", "大厅/排行", "地图名、难度、缩略图", "地图选择/预览 UI", "W14 联调"),
    ], [2.6, 3.4, 5.0, 3.2, 2.6], 7.5, caption_text="表 1-4　B-地图系统与队友的接口")

    para(doc, "开发环境沿用我在 10 月 10 日环境作业里已经验证过的工具链，今晚没有重新装环境。下面的截图能看到版本号：Git 2.54、JDK 21.0.11、Kotlin 2.4.21、Gradle 9.8.1、Tiled 1.12.2、Python 3.12.10、Pygame 2.6.1、EA 17.2。")
    two_images(doc, os.path.join(ASSETS, "env", "fig-01-env-check.png"),
               os.path.join(ASSETS, "env", "fig-04-kotlin-run.png"), 7.4,
               "图 1-1　开发环境验证（左：工具版本；右：Kotlin 编译运行）")
    R.add_table(doc, ["工具", "版本", "用途"], [
        ("Git", "2.54.0", "版本控制"), ("JDK", "21.0.11 LTS", "Kotlin/JVM"),
        ("Kotlin", "2.4.21", "桌面端"), ("Gradle", "9.8.1", "构建"),
        ("Tiled", "1.12.2", "地图编辑"), ("Python", "3.12.10", "离线生成/校验"),
        ("Pygame", "2.6.1", "备选原型"), ("IDEA CE", "2025.2.6.2", "IDE"),
        ("EA", "17.2.1721", "UML 建模"), ("Node", "24.16.0", "H5 构建"),
    ], [4.0, 4.6, 8.0], 7.5, caption_text="表 1-5　开发环境与用途")


def chapter2(doc):
    R.h(doc, "二、协作与项目计划", 1, page_break=True)
    para(doc, "计划要能落到分支、任务、日期和风险上，不能只写一张时间表。今晚我先把本地 Git 基线和 EA 模型做出来，后续按分支提交。")

    R.h(doc, "2.1 Git 仓库与协作", 2)
    para(doc, "本地仓库已经初始化：main 放稳定基线，develop 做集成，feature/yaoshuai-map 提交 B 模块文档。今晚有 4 次真实提交，提交信息按 Conventional Commits 写；GitHub 远程仓库由我创建后 push，报告里只写本地真实记录，不编 PR 和 CI 运行。")
    R.add_table(doc, ["分支", "用途", "当前提交"], [
        ("main", "稳定基线", "1c19f9c chore: 初始化仓库与目录结构"),
        ("develop", "集成", "c3662d9 docs(plan): 添加实验一项目计划初稿"),
        ("feature/yaoshuai-map", "B 模块", "7b9c51a docs(map): 添加 B-地图系统规范与接口\n2702ab4 docs(ai): 添加实验一 AI 使用记录"),
    ], [3.8, 2.6, 10.4], 8, caption_text="表 2-1　本地 Git 分支与提交")
    para(doc, "后续规则：main/develop 保护，feature 分支走 Pull Request + 1 人评审；提交用 feat/fix/docs/test/refactor/chore 前缀。GitHub Actions 计划在 W11 接入，先跑 Kotlin 构建和地图 schema 校验；今晚没有跑，所以不写运行记录。")

    R.h(doc, "2.2 WBS", 2)
    para(doc, "团队总量按 200 人时估，L3 任务控制在 4~16 人时。WBS 做到 L1 项目 → L2 阶段 → L3 任务包，B 的 4.4 再拆到 L4；这样别人拿到表知道做什么，也知道做到什么算完。")
    R.add_figure(doc, os.path.join(ASSETS, "ea", "fig2-1-wbs.png"),
                 "图 2-1　项目 WBS（编码阶段与 B 模块展开；完整 L3 见表 2-2）", 11.5)
    wbs = [
        ("1.1", "环境与工具验证", "4", "全员", "环境截图/版本表"),
        ("1.2", "Git 仓库与分支模型", "4", "姚帅", "仓库/分支/README"),
        ("1.3", "WBS、进度与成本", "4", "姚帅", "WBS/甘特/预算"),
        ("1.4", "计划书统稿与评审", "6", "姚帅+全员", "计划书/评审记录"),
        ("2.1", "游戏规则与用例", "6", "杨宇航", "规则说明/用例图"),
        ("2.2", "战斗、道具需求", "8", "姚于轩/杨旭", "需求清单"),
        ("2.3", "地图与数据需求", "4", "姚帅", "地图规范/数据字典"),
        ("2.4", "SRS 与追踪矩阵", "10", "杨旭/杨宁宁", "SRS/矩阵"),
        ("3.1", "总体架构与通信协议", "8", "杨宇航", "架构图/协议"),
        ("3.2", "地图系统设计", "6", "姚帅", "类图/接口/规范"),
        ("3.3", "战斗与道具设计", "8", "姚于轩/杨旭", "类图/状态机"),
        ("3.4", "房间/大厅/数据设计", "6", "杨宁宁", "ERD/API"),
        ("3.5", "测试与部署设计", "6", "杨旭", "测试计划/部署图"),
        ("4.1", "战斗引擎", "14", "姚于轩", "移动/射击/碰撞"),
        ("4.2", "地图渲染", "8", "姚帅", "TMX 加载/多地形"),
        ("4.3", "地图碰撞与地形效果", "8", "姚帅", "碰撞查询/砖墙破坏"),
        ("4.4", "地图编辑器与 AI 生成", "16", "姚帅", "Tiled 工程/校验器/生成器"),
        ("4.5", "房间服务与同步", "14", "杨宇航", "WS/房间/观战"),
        ("4.6", "道具与升级树", "12", "杨旭", "道具/升级"),
        ("4.7", "大厅/战队 H5", "12", "杨宁宁", "登录/战队/排行"),
        ("5.1", "单元测试", "6", "杨旭", "单测/覆盖率"),
        ("5.2", "联机集成测试", "6", "杨宇航", "集成测试报告"),
        ("5.3", "性能与兼容性", "4", "姚于轩", "帧率/延迟记录"),
        ("5.4", "打包、部署与演示", "6", "杨宁宁", "安装包/部署说明"),
        ("6.1", "周会与评审", "4", "姚帅", "会议/评审记录"),
        ("6.2", "文档与答辩", "10", "姚帅+全员", "报告/PPT"),
    ]
    R.add_table(doc, ["WBS", "任务", "工时", "责任人", "交付物"], wbs,
                [1.2, 5.2, 1.4, 3.4, 5.6], 7.2, caption_text="表 2-2　WBS 任务分解与工时（L3）")
    R.add_table(doc, ["L4", "任务", "工时", "交付物"], [
        ("4.4.1", "Tiled 工程、图层与图块属性规范", "4", "maps/、map-spec.md"),
        ("4.4.2", "地图校验 CLI（连通/基地/比例）", "4", "mapcheck + 校验报告"),
        ("4.4.3", "AI 地图生成（生成器 + 难度参数）", "8", "生成器 + 30 张样本"),
    ], [2.0, 8.8, 1.8, 4.2], 8, caption_text="表 2-3　B 模块 4.4 的 L4 分解")
    para(doc, "三项校验：15 项功能都能在 4.x 找到归属；工时最大 16、最小 4，B 42 + 管理 6 = 48，其他人 36~40；依赖方向是 2.x → 3.x → 4.x，没有倒置。WBS 的不足是只把 B 的 4.4 拆到 L4，其他模块还停在 L3，后续实验二再补 WBS 词典。")

    R.h(doc, "2.3 进度与关键路径", 2)
    para(doc, "进度按第 10~17 周排，五个里程碑：M1 计划/仓库/EA、M2 需求、M3 设计、M4 功能冻结、M5 交付答辩。关键路径是“计划→需求→设计→战斗/地图/房间编码→联机集成→测试→答辩”，五个阶段基本串行，所以 W16 后留 2 天缓冲。")
    R.add_figure(doc, os.path.join(ASSETS, "charts", "fig2-2-gantt.png"),
                 "图 2-2　项目甘特图（W10~W17，含里程碑与 2 天缓冲）", 16.0)
    R.add_table(doc, ["里程碑", "周次", "日期", "交付物", "完成标准"], [
        ("M1 计划基线", "W10", "2026-11-13", "计划书、仓库、EA 图", "初稿提交，仓库可访问"),
        ("M2 需求基线", "W12", "2026-11-27", "SRS、用例、地图规范 v1", "5 人评审确认"),
        ("M3 设计基线", "W13", "2026-12-04", "架构、类图、协议", "接口冻结"),
        ("M4 功能冻结", "W16", "2026-12-25", "可联机演示版本", "核心功能 + 测试通过"),
        ("M5 交付答辩", "W17", "2027-01-05", "安装包、报告、PPT", "演示/答辩通过"),
    ], [3.0, 1.6, 2.8, 5.0, 4.4], 8, caption_text="表 2-4　里程碑与完成标准")
    para(doc, "B 的渲染/碰撞在关键路径上，编辑器/AI 生成有 2 天浮动。地图规范在 W11 冻结，先给 A 一张 stub 地图，避免 A 等我；如果 W14 碰撞没完成，先砍 AI 生成，保联机演示。")

    R.h(doc, "2.4 风险", 2)
    para(doc, "风险按概率 × 影响排，最需要盯的是 R1（地图规范和 A 的碰撞接口）和 R4（Kotlin/LibGDX 学习曲线）。R1 的应对是 W11 冻结 schema、先给 stub 地图；R4 的应对是 W13 先做渲染 spike，Pygame 只作备选。")
    R.add_figure(doc, os.path.join(ASSETS, "charts", "fig2-3-risk.png"),
                 "图 2-3　项目风险矩阵（概率 × 影响，风险值 = 概率 × 影响）", 14.5)
    R.add_table(doc, ["编号", "风险", "概率", "影响", "值", "应对"], [
        ("R1", "地图规范与 A 的碰撞接口不一致", "4", "4", "16", "W11 冻结 schema；先给 stub 地图；每周接口对齐"),
        ("R2", "Tiled 版本/格式差异", "3", "3", "9", "固定 Tiled 1.12.2；schema 校验；CI mapcheck"),
        ("R3", "AI 生成地图不平衡/不可玩", "3", "4", "12", "生成器 + 校验器 + 试玩；失败退回模板"),
        ("R4", "Kotlin/LibGDX 学习曲线", "4", "3", "12", "W13 先做渲染 spike；Pygame 仅备选"),
        ("R5", "map hash/联机同步不一致", "3", "4", "12", "canonical JSON + hash + version；集成测试"),
        ("R6", "考试周与进度冲突", "4", "3", "12", "2 天缓冲；必要时砍 AI 生成"),
        ("R7", "素材版权", "2", "3", "6", "原创/CC0 素材，记录来源"),
    ], [1.0, 4.8, 1.2, 1.2, 1.2, 7.4], 7.5, caption_text="表 2-5　风险登记册")

    R.h(doc, "2.5 质量、成本与配置", 2)
    para(doc, "质量目标不追求“全绿”，先保地图校验、帧率和联机稳定；成本按 200 人时 × 30 元折算，现金只留 AI API 100 元；配置基线是 M2 需求、M3 设计、M4 代码，变更走 Issue → 影响分析 → 组长 + 1 名组员审批。")
    R.add_table(doc, ["类别", "内容", "指标/说明"], [
        ("质量", "单元测试覆盖率", "≥60%（地图模块 ≥70%）"),
        ("质量", "地图校验", "发布图 100% 通过"),
        ("质量", "帧率/加载", "1280×720 60 FPS；加载 <200ms"),
        ("质量", "AI 生成", "30 张/档，修复后 100% 通过，单张 <2s"),
        ("质量", "联机稳定", "10 局无崩溃；ktlint/detekt 0 error"),
        ("成本", "人力", "200h × 30 元 = 6,000 元"),
        ("成本", "AI API", "约 100 元；每人配额 20 元"),
        ("成本", "工具/合计", "0 元（教育/开源）；合计 6,100 元"),
        ("配置", "分支/基线", "main/develop/feature；M2/M3/M4 基线"),
        ("配置", "变更", "Issue→影响分析→组长+1 人→实施→回归"),
    ], [1.6, 4.8, 10.4], 7.5, caption_text="表 2-6　质量、成本与配置基线")
    R.add_table(doc, ["项目", "状态", "证据 / 下一步"], [
        ("实验一报告", "已完成初稿", "本 PDF；审后修改"),
        ("本地 Git", "已完成", "main/develop/feature + 4 次提交"),
        ("EA 工程", "已完成", "model/TankBattle.qea，5 张图"),
        ("地图规范", "已完成初稿", "docs/map-spec.md；W11 冻结 v1"),
        ("AI 记录", "已完成", "docs/ai-log.md，6 条"),
        ("风险/质量/成本", "已完成初稿", "表 2-5、2-6；W12 复盘"),
        ("GitHub 远程", "进行中", "组长今晚 push"),
        ("游戏代码", "计划 W13", "不在实验一塞半成品"),
    ], [3.4, 3.0, 10.4], 7.8, caption_text="表 2-7　实验一交付自检")


def chapter3(doc):
    R.h(doc, "三、我的模块：地图系统", 1)
    para(doc, "地图系统是 B 的核心，也是 A 的碰撞和 C 的同步的上游。我先定地图数据和 MapService 接口，再谈渲染、编辑器和 AI 生成；顺序反了就会返工。")

    R.h(doc, "3.1 需求与总体结构", 2)
    para(doc, "桌面端由 A 战斗引擎、B 地图系统、D 道具升级三块组成，C 是 WebSocket 服务端，E 是 H5 大厅。B 向下读 Tiled 地图，向上给 A/D 提供地形查询，向 C 提供地图元数据，向 E 提供地图摘要。")
    R.add_figure(doc, os.path.join(ASSETS, "ea", "fig3-1-component.png"),
                 "图 3-1　系统构件图（A/B/D 桌面端、C 服务端、E H5、地图契约与 AI）", 14.8)
    para(doc, "地图系统的参与者有三个：玩家加载/预览/同步地图，地图作者用 Tiled 编辑/校验/查看信息，AI 服务给难度参数和校验解释。游戏端不重复做编辑器 UI，只做加载、预览和校验入口。")
    R.add_figure(doc, os.path.join(ASSETS, "ea", "fig3-2-usecase.png"),
                 "图 3-2　地图系统用例图（玩家/地图作者/AI 服务）", 13.5)

    R.h(doc, "3.2 地图规范与数据", 2)
    para(doc, "地图用 Tiled 正交格式，26×26 格、单格 16×16px，分 terrain/decor/objects 三层；图块属性写在 Tiled custom properties 里，加载器按属性生成 TerrainEffect，不在代码里写死地形判断。")
    R.add_table(doc, ["地形", "碰撞", "子弹", "特性"], [
        ("空地", "可通行", "可过", "—"),
        ("砖墙", "阻挡", "命中破坏", "HP 1；普通子弹可破"),
        ("钢墙", "阻挡", "命中", "HP 2；power≥2 才破"),
        ("水域", "阻挡", "可过", "坦克不可进"),
        ("冰面", "可通行", "可过", "摩擦低，滑行"),
        ("草丛", "可通行", "可过", "绘制在坦克上层，遮挡"),
        ("基地", "阻挡", "命中判负", "不可破坏"),
    ], [2.4, 3.0, 3.0, 8.4], 8, caption_text="表 3-1　地形类型与属性")
    doc.add_page_break()
    R.add_table(doc, ["字段/方法", "说明"], [
        ("map_id / name / version", "地图标识、显示名、版本；联机比对"),
        ("seed / difficulty / hash", "生成种子、难度、静态地图 SHA-256 前 16 位"),
        ("load(mapId, version)", "加载并缓存地图"),
        ("isBlocked(rect, mover)", "坦克 AABB 与地形碰撞"),
        ("terrainAt(cell)", "摩擦、遮挡、可通行"),
        ("hitBullet(cell, power)", "子弹命中；返回是否破坏"),
        ("spawnPoints() / freeCells()", "出生点；可放道具的空格"),
    ], [6.0, 10.8], 8, caption_text="表 3-2　地图元数据与 MapService 接口")
    para(doc, "地图的静态部分用 canonical JSON 算 hash，动态部分（砖墙破坏）由 C 广播 MAP_STATE 事件，回放存“初始地图 + 事件序列”。这样联机两端加载的是同一张图，回放也不用存整张地图。")

    R.h(doc, "3.3 渲染与碰撞", 2)
    para(doc, "渲染用 LibGDX 的 TmxMapLoader + OrthogonalTiledMapRenderer，按 terrain/decor 两层绘制，草丛在坦克上层；水面/冰面做两帧动画，摄像机按 1280×720 视口裁剪。26×26 的地图很小，60 FPS 不是难点，难点是图层顺序和碰撞一致性。")
    R.add_figure(doc, os.path.join(ASSETS, "ea", "fig3-3-class.png"),
                 "图 3-3　地图系统类图（TileMap/MapService/Collision/Validator/Generator）", 16.0)
    para(doc, "碰撞只做地形：坦克按 X/Y 轴分离移动，每轴移动前用 AABB 查目标格，避免高速穿透；砖墙普通子弹 1 发破坏，钢墙 power≥2 才破，水域挡坦克不挡子弹，冰面降低摩擦，草丛不阻挡但绘制在坦克上层。A 负责坦克-坦克、坦克-子弹，B 只回答“这个格能不能走/这颗子弹打中了什么”。")

    R.h(doc, "3.4 编辑器与 AI 生成", 2)
    para(doc, "编辑端用 Tiled 1.12.2，不重复开发通用编辑器 UI：我提供 tiled-project、tileset、出生点/基地模板和 custom properties，地图作者在 Tiled 里画，保存 .tmx；游戏内只做加载、预览和 mapcheck 校验。这个取舍省掉了按钮、撤销、图层面板等大量工作，代价是编辑体验依赖 Tiled。")
    R.add_figure(doc, os.path.join(ASSETS, "ea", "fig3-4-activity.png"),
                 "图 3-4　地图编辑与 AI 生成活动图（生成/编辑→校验→通过/修复→保存）", 16.0)
    para(doc, "AI 生成不让大模型直接吐瓦片，而是“生成器 + 校验器 + LLM 只做参数/解释”：生成器用 BSP/细胞自动机/模板出候选，校验器查连通、基地保护、地形比例和出生点公平，LLM 只把难度描述转成参数、解释校验报告；API 不可用就退回参数表。这样即使模型胡说，也不会产出不可玩的地图。")
    R.add_table(doc, ["检查项", "规则", "目标"], [
        ("连通性", "每个出生点到基地存在通路", "100%"),
        ("基地保护", "基地周围 ≥6 块砖，出生点到基地无直线通视", "100%"),
        ("地形比例", "砖 15~30%、钢 5~12%、水 ≤10%、冰 ≤8%、草 5~15%", "全部在区间"),
        ("出生点公平", "路径长度差 ≤15%，掩体比例差 ≤10%", "通过"),
        ("生成效率", "每档 30 张，单张 <2s，修复后 100% 通过", "达标"),
        ("试玩", "3 位同学对公平性打分 ≥3.5/5", "W16 验证"),
    ], [3.0, 9.8, 4.0], 8, caption_text="表 3-3　AI 地图生成校验指标")

    R.h(doc, "3.5 接口、创新与取舍", 2)
    para(doc, "接口在表 1-4 已经列过：A 调 isBlocked/terrainAt/hitBullet，C 拿 map_id/version/hash 和 MAP_STATE，D 用 freeCells()，E 拿地图摘要。我的原则是 B 只提供查询和事件，不反向调用 A/C/D/E 的业务逻辑，避免循环依赖。")
    para(doc, "创新点我只敢写三个：① AI 生成地图的“生成器 + 校验器 + 试玩”闭环，这是产品级雏形，但还没跑够 30 张样本，W16 才能给结论；② 地图即数据，seed/hash/事件回放让联机、回放、编辑器共用一份地图；③ 用 Tiled 做编辑端、自己不造编辑器，这是工程取舍，不算创新。前两个有价值，第三个只是省时间。")
    para(doc, "我知道的最大风险是：地图规范还没和 A 实际联调。W11 我会先给 A 一张 stub 地图和接口签名，W13 渲染 spike 时再改；如果拖到 W14 才联调，A 的战斗循环会被我卡住。")

    R.h(doc, "3.6 阶段验收与联调节点", 2)
    para(doc, "地图模块按检查点验收，每个点都有可检查的产物；这些点也是我和 A/C/D/E 的同步点，避免到 W16 才发现接口对不上。")
    R.add_table(doc, ["检查点", "时间", "交付物", "验收"], [
        ("C1 规范冻结", "W11", "map-spec v1 + stub 地图", "A/C/D/E 确认接口签名"),
        ("C2 渲染 spike", "W13", "TMX 加载 + 5 地形 Demo", "60 FPS、无缺块"),
        ("C3 碰撞/编辑器", "W15", "MapService + 20 条单测 + mapcheck", "砖/钢/水/冰/草行为正确"),
        ("C4 AI/联调", "W16", "30 张/档 + map hash", "100% 通过，联机一致"),
        ("C5 交付", "W17", "Demo + 测试报告", "答辩演示"),
    ], [3.2, 1.6, 6.4, 5.6], 7.8, caption_text="表 3-4　地图模块阶段验收")


def chapter4(doc):
    R.h(doc, "四、个人任务与提交", 1)
    para(doc, "这一章只写我自己的任务、时间和提交方式，不重复团队计划。")

    R.h(doc, "4.1 个人任务卡", 2)
    R.add_table(doc, ["WBS", "任务", "工时", "交付物", "周次", "依赖"], [
        ("1.2", "仓库/分支", "2", "仓库/README", "W10", "—"),
        ("1.3", "WBS/进度/成本", "2", "WBS/甘特", "W10", "分工"),
        ("1.4", "计划统稿/评审", "2", "本报告/评审", "W10", "全员"),
        ("2.3", "地图/数据需求", "4", "map-spec v1", "W11", "规则"),
        ("3.2", "地图设计", "6", "类图/接口", "W12", "需求"),
        ("4.2", "地图渲染", "8", "TMX 加载/5 地形", "W13", "设计"),
        ("4.3", "地图碰撞", "8", "MapService/单测", "W14", "渲染"),
        ("4.4", "编辑器 + AI 生成", "16", "Tiled/校验/生成器", "W15-16", "碰撞/接口"),
        ("", "合计", "48", "B 42 + 管理 6", "", ""),
    ], [1.2, 5.0, 1.4, 5.2, 1.8, 2.2], 7.8, caption_text="表 4-1　个人任务卡（RACI 中的 R）")

    R.h(doc, "4.2 W10~W17 排期", 2)
    R.add_table(doc, ["周次", "我的任务", "交付物", "风险/备注"], [
        ("W10", "计划书、Git 仓库、EA 图、环境核对", "初稿、EA 工程", "今晚先交初稿"),
        ("W11", "地图规范 v1、地形清单、接口契约", "map-spec.md", "先给 A stub 地图"),
        ("W12", "类图/顺序图、TMX schema、校验规则", "设计图、schema", "M2 需求基线"),
        ("W13", "TMX 加载 + 5 地形渲染 spike", "地图 Demo", "Kotlin/LibGDX 风险"),
        ("W14", "碰撞、砖墙破坏、冰面/水域/草丛", "MapService + 单测", "关键路径"),
        ("W15", "Tiled 工程、校验 CLI", "可校验地图", "M3 设计基线"),
        ("W16", "AI 生成 + map hash + 联机集成", "生成器/校验报告", "30 张样本"),
        ("W17", "测试、演示、答辩", "测试报告/PPT", "M5 交付"),
    ], [1.6, 7.0, 4.4, 3.8], 7.8, caption_text="表 4-2　个人周排期")

    R.h(doc, "4.3 AI 使用与核验", 2)
    para(doc, "AI 用在报告结构、WBS 初稿、地图 schema、EA 图布局和文字润色；工时、接口、风险等级、图件和最终结论由我核对。EA 图是在 EA 17.2 工程里建立并导出的，AI 不直接生成提交用的模型图；详细 Prompt 记录在 docs/ai-log.md。")
    R.add_table(doc, ["编号", "场景", "AI 输出", "我的处理", "结论"], [
        ("A-01", "任务解读", "B 的 3 项功能/边界", "确认角色，删无关调研", "采纳（改后）"),
        ("A-02", "技术栈", "Kotlin/LibGDX vs Pygame", "选 Kotlin+LibGDX+Tiled", "采纳"),
        ("A-03", "文件名", "三套命名", "选“实验一”方案", "采纳"),
        ("A-04", "WBS/工时", "26 项 L3/200h", "按组内分工改责任人", "部分采纳"),
        ("A-05", "地图规范", "TMX/MapService/AI 校验", "确认 A/B 边界与 30 张指标", "采纳（改后）"),
        ("A-06", "报告结构", "12~15 页目录", "删竞品/三套环境/未发生 CI", "采纳（改后）"),
    ], [1.4, 3.0, 5.6, 4.6, 2.2], 7.5, caption_text="表 4-3　AI 使用记录摘要")

    R.h(doc, "4.4 提交说明", 2)
    para(doc, "PDF 单独提交，文件名按“班级-学号-姓名-项目-实验”命名；zip 等我审完 PDF 后再打，不提前打包。EA 工程用 EA 17.2 打开，报告源和生成脚本在 src/，地图规范在 docs/。")
    R.add_table(doc, ["提交物", "文件名/位置", "说明"], [
        ("PDF", "cs24104-2024210622-姚帅-坦克大战联机复刻-实验一软件项目计划.pdf", "单独提交"),
        ("zip", "同名 + -源码.zip", "审后由组长打包"),
        ("EA", "model/TankBattle.qea", "EA 17.2 打开"),
        ("仓库", "GitHub cs24104-TankBattle", "组长上传"),
        ("AI 记录", "docs/ai-log.md", "6 条四件套"),
        ("报告源", "report/docx + src/", "可复现"),
    ], [2.6, 10.4, 3.8], 7.8, caption_text="表 4-4　提交清单")
    para(doc, "下一步：W11 先把地图规范 v1 和 A 的接口签名定下来，给 A 一张 stub 地图；W13 开始写代码，W16 用 30 张地图验证 AI 生成；W17 答辩时现场打开 EA 工程和地图 Demo，讲清楚 WBS、碰撞边界和 AI 校验。")
    R.body(doc, "（报告完）", indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)


def main():
    doc = Document()
    R.set_doc_defaults(doc)
    sec = doc.sections[0]
    R.set_section_layout(sec)
    sec.different_first_page_header_footer = True
    R.add_header_footer(sec, "软件工程基础（2024 版）· 实验一 软件项目计划")
    cover(doc)
    toc(doc)
    chapter1(doc)
    chapter2(doc)
    chapter3(doc)
    chapter4(doc)
    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
