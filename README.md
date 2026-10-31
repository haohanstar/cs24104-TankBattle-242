# cs24104-TankBattle

软件工程基础（2024 版）课程实验项目：**坦克大战·联机复刻**。

| 项目 | 内容 |
|---|---|
| 组别 | cs24104 / 计科 242 |
| 项目 | 坦克大战·联机复刻（网游方向） |
| 应用端 | 桌面端 + Web 后端 + 移动端 H5 |
| 组长 | 姚帅（2024210622，B-地图系统 / 桌面端） |
| 组员 | 姚于轩（A-战斗引擎）、杨宇航（C-对战房间）、杨旭（D-道具升级）、杨宁宁（E-大厅战队） |
| 桌面端主栈 | Kotlin 2.4.21 + JDK 21 + Gradle 9.8.1 + LibGDX + Tiled 1.12.2 |
| 工具链 | Python 3.12（离线地图生成/校验）、Git、EA 17.2、IntelliJ IDEA CE |

## 目录

```
.
├─ README.md
├─ .gitignore
├─ docs/                 项目计划、地图规范、AI 记录
├─ report/               实验一交付件：报告 docx/pdf、源码 zip
│  └─ assets/            环境截图、EA 导出图、甘特图、风险矩阵
├─ model/                EA 17.2 工程与导出图
│  ├─ TankBattle.qea
│  └─ images/
├─ src/                  报告/EA/图表生成脚本（可复现）
└─ maps/                 地图 schema 与示例
```

## 实验一交付物

- `report/坦克大战实验一报告.docx` / `report/cs24104-2024210622-姚帅-坦克大战联机复刻-实验一软件项目计划.pdf`：实验一软件项目计划初稿（14 页）。
- `report/cs24104-2024210622-姚帅-坦克大战联机复刻-实验一软件项目计划-源码.zip`：源码包，审完 PDF 后由 `python src/make_zip.py` 生成到 `report/`。
- `model/TankBattle.qea`：EA 17.2 工程，含 WBS、构件、用例、类图、活动图。
- `report/assets/`：环境截图、EA 导出图、甘特图、风险矩阵。
- `src/`：报告、图表、EA 工程的生成脚本；`src/make_zip.py` 在审完 PDF 后再运行。
- `docs/`：项目计划、地图规范、AI 使用记录。

**个人任务清单与操作步骤不进仓库**，保存在本地工作区，避免公开个人安排。

## 打开方式

- 报告：用 Word 打开 `.docx`；`.pdf` 为最终排版。
- EA 工程：用 Enterprise Architect 17.2 打开 `model/TankBattle.qea`，在 Project Browser 中展开 `01 项目计划` / `02 需求` / `03 设计`，双击图查看。
- 图表复现：`python src/gen_charts.py`；报告复现：`python src/build_report.py` 后用 Word 更新目录并导出 PDF。

## 上传到 GitHub（组长操作）

1. 在 GitHub 新建空仓库 `cs24104-TankBattle`（不要勾选 README/.gitignore/License）。
2. 在本目录执行：

```powershell
git remote add origin https://github.com/<你的GitHub用户名>/cs24104-TankBattle.git
git push -u origin main
git push origin develop
git push origin feature/yaoshuai-map
```

3. 在 GitHub 仓库 Settings → Branches 里给 `main`、`develop` 加保护规则；后续 feature 分支走 Pull Request。

## 说明

- 本仓库不含第三方库、构建产物或 IDE 缓存；LibGDX/Tiled/EA 等工具按环境手册安装。
- 实验一为项目计划阶段，游戏源码从实验四开始进入本仓库。
