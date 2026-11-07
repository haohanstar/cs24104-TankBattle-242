# 坦克大战·联机复刻 软件需求规格说明书（SRS 初稿）

| 项 | 内容 |
|---|---|
| 项目名称 | 坦克大战·联机复刻 |
| 组别 / 班级 | cs24104 / 计科 242 |
| 组长 / 编写人 | 姚帅（2024210622），B-地图系统 |
| 版本 | v0.1（实验二第 1 次课初稿） |
| 日期 | 2026-11-07 |
| 配套文件 | `docs/02-需求清单.md`、`docs/02-DFD.md`、`docs/02-调研记录.md`、`model/TankBattle.qea` |

本稿按 GB/T 8567 的八章结构写，第 1 次课只把第 1~8 章写成可用版本：功能需求和非功能需求写全，接口和数据字典写到字段级，追踪矩阵先给出主干。第 2 次课补量化测量脚本、活动图/状态图/包图、评审闭环和 MDG 导出的代码框架。

## 1. 引言

### 1.1 编写目的

这份 SRS 把“我们要做一个什么样的联机坦克游戏”写成能验收的条文，给三类人看：组内 5 个人照着它拆任务、写代码；老师按它判断需求分析做得够不够；答辩时抽一条需求，能顺着它追到用例、类、接口和测试。

### 1.2 项目范围

本项目是经典《坦克大战》的联机复刻，保留砖墙、钢墙、水域、冰面、草丛、基地六种地形，加上地图编辑、AI 地图生成、道具升级、房间观战、大厅战队这些联机功能。交付形态是三类应用端：桌面端 3 个（A 战斗引擎、B 地图系统、D 道具升级）、Web 后端 1 个（C 对战房间）、移动端 H5 1 个（E 大厅战队）。

本期（实验二第 1 次课）的范围就是 `docs/02-需求清单.md` 里的 15 条功能需求和 8 条非功能需求，覆盖 4 个角色（玩家、观战者、管理员、AI 服务）。

明确不做的事：3D 地图、VR/AR；在线支付和商城；语音聊天；第三方版权素材；跨平台账号打通。这几项在需求评审时不再讨论，谁提新功能先对照这一节，超范围的不进 SRS。

### 1.3 术语与缩略语

| 术语 | 含义 |
|---|---|
| TMX | Tiled 地图编辑器导出的 XML 地图文件格式 |
| TileMap | 内存中的地图对象，含每格类型、生命值、属性 |
| `MapService` | B 模块对外提供的 7 个地图查询/事件方法 |
| `mapcheck` | B 模块的地图校验 CLI，按规则检查 `.tmx` |
| AABB | 轴对齐包围盒，坦克与地形的碰撞判定方式 |
| tick | 服务端逻辑帧，本项目 20 tick/s |
| `hash` | 地图规范化 JSON 的 SHA-256 前 16 位，用于两端比对 |
| `STATE_SNAPSHOT` | 服务端下发的状态快照消息 |
| `MAP_STATE` | 地图破坏状态广播消息 |
| AI 服务 | 外部大模型/算法服务，提供瞄准、生成、解说、匹配 |

### 1.4 参考资料

| 编号 | 文件 | 用途 |
|---|---|---|
| R1 | `docs/01-项目计划书.md` | 分工、WBS、里程碑、质量目标 |
| R2 | `docs/map-spec.md` | 地图格式、地形属性、`MapService` 接口 |
| R3 | `maps/schema/map.schema.json` | 地图 JSON schema |
| R4 | `docs/协作规范.md` | 分支、提交、接口变更流程 |
| R5 | `docs/02-需求清单.md` | 15 FR + 8 NFR |
| R6 | `docs/02-DFD.md` | DFD 分层与数据字典 |
| R7 | Enterprise Architect 17.2 | 模型图绘制工具 |

### 1.5 读者对象

组内 5 名开发同学（按模块读第 3、5、6 章）；课程老师与助教（读第 1~4 章、第 7 章）；答辩评委（按第 7 章的追踪链路抽查）。

## 2. 总体描述

### 2.1 产品视角

系统不是纯客户端游戏，而是“客户端 + 权威服务端”的结构：服务端判定位置、血量、胜负，客户端只做输入采集和表现。这样做的直接原因是作弊——如果血量在客户端算，改一个内存值就能无敌，`NFR-06` 就没法验收。

模块划分和依赖关系：

- A 战斗引擎（桌面端）：移动、射击、碰撞、武器、AI 瞄准。它判断坦克-坦克、坦克-子弹、子弹-子弹三类碰撞，地形判断一律调 B。
- B 地图系统（桌面端 + Python 工具）：地图加载、五类地形渲染、地形碰撞查询、地图编辑器、`mapcheck`、AI 地图生成。
- C 对战房间（Web 后端）：房间、匹配、WebSocket 同步、断线重连、观战、回放、AI 解说。
- D 道具升级（桌面端）：道具生成/拾取/效果、升级树、AI 投放。
- E 大厅战队（H5）：登录、好友、组队、战队、排行榜、锦标赛、AI 匹配。

依赖方向是单向的：A/D 依赖 B 的地形查询；C 依赖 B 的元数据与破坏事件；E 只读 C 的接口和 B 的地图摘要。B 不反向依赖 A/C/D/E，这条在接口评审时定死了，避免出现循环依赖。

### 2.2 用户角色

| 角色 | 特征 | 关心什么 | 对应需求 |
|---|---|---|---|
| 玩家 | 学生玩家为主，桌面端与 H5 都用 | 操作跟手、匹配快、掉线能回来、道具别破坏公平 | FR-01~FR-09、FR-11~FR-15 |
| 观战者 | 不参与战斗，看直播或回放 | 画面跟得上、能看到双方状态、回放能拖时间轴 | FR-10 |
| 管理员 | 组长或指定同学兼任 | 地图能校验、违规能处理 | FR-06、FR-10、FR-13、FR-14 |
| AI 服务 | 不是人，是系统调用的外部服务 | 请求要能降级，超时不能把对局拖死 | FR-04、FR-07、FR-13、FR-15 |

### 2.3 运行环境

| 端 | 环境 | 版本 |
|---|---|---|
| 桌面端 | Windows 10/11 x64，JDK 21（Temurin 21.0.11），Kotlin 2.4.21，Gradle 9.8.1，LibGDX，Tiled 1.12.2 | 开发机实测 |
| 服务端 | JDK 21 + Spring Boot + WebSocket + Netty，单机部署（开发机 + 一台云主机） | — |
| 移动端 H5 | Chrome / Edge 最新版，Vue3 + WebSocket + ECharts，宽度 320/375/414 | — |
| 工具 | Python 3.12（地图生成与校验），Enterprise Architect 17.2 | — |

### 2.4 设计与实现约束

1. 地图坐标一律用格坐标（`cell`），像素只在渲染层换算，避免 A/B 两边坐标系不一致。
2. 地图默认 26×26 格、单格 16×16 px。尺寸可变，但只能在 13~52 之间，且必须是 schema 允许的值。
3. 地图元数据字段名统一用下划线（`map_id`、`map_version`），不允许出现 `mapId` 这种驼峰写法，接口映射在服务端做。
4. 地形判断只有 B 一处实现。A 若自己写一套 `if (tile == BRICK) return true`，接口评审直接打回。
5. 服务端权威：客户端上报的坐标只作为预测，最终以 `STATE_SNAPSHOT` 为准。
6. AI 相关功能一律可关闭、可降级，不能成为开局的前置条件。

### 2.5 假设与依赖

- 假设局域网环境（同一间实验室）延迟 <20 ms，`NFR-01` 的 100 ms 按这个前提写。
- 假设单台云主机能撑 10 房间 / 50 玩家；撑不住就砍到 6 房间 / 30 玩家，并在答辩时说明。
- 依赖 Tiled 1.12.2 的 `.tmx` 格式；Tiled 升级会导致图块属性读取方式变化，这是风险 R2。
- 依赖外部 AI API 的可用性；不可用时按 `NFR-08` 降级。
- 依赖 GitHub 仓库与组内分支约定（`feature/<姓名拼音>-<模块>`）。

## 3. 功能需求

### 3.1 需求总览

15 条功能需求按角色分：A 4 条（FR-01~04）、B 3 条（FR-05~07）、C 3 条（FR-08~10）、D 3 条（FR-11~13）、E 2 条（FR-14~15）。每条需求的完整条目（场景、输入、输出、验收判据、来源、用例）在 `docs/02-需求清单.md`，本章按模块写清边界和关键约束，不重复抄表。

### 3.2 A 战斗引擎

**FR-01 移动与地形碰撞。** 坦克按 8 方向移动，X/Y 轴分轴检测，每轴移动前查目标格。地形判断调用 `MapService.isBlocked(rect, mover)` 与 `terrainAt(cell)`，A 侧不写地形分支。验收要求 8 方向可移动、8 px/帧 高速移动 20 次 0 穿透、冰面松键后至少滑行半格。

**FR-02 射击与三类碰撞。** 坦克-坦克、坦克-子弹、子弹-子弹由 A 判定；子弹-地形交 `hitBullet(cell, power)`。三类各 10 组用例，判定与预期一致；2 格/帧的子弹不穿透 1 格砖墙。

**FR-03 多武器。** 散弹（3 发/单发伤害 1）、激光（穿 1 层砖、冷却 1.5 s）、追踪导弹（30° 内自动修正、命中率 ≥70%）。参数全部来自配置表，改配置不改代码。

**FR-04 AI 瞄准。** 只输出射击方向角，不接管移动与碰撞。匀速横移目标 50 次射击命中率 ≥60%（直线瞄准同条件 ≤35%）；接口 500 ms 超时退回直线瞄准。

### 3.3 B 地图系统

**FR-05 地图加载与渲染。** 输入 `map_id`/`version`/`hash` 与 `.tmx`，输出 `TileMap` 与渲染结果。三层（`terrain`/`decor`/`objects`）；加载前比对 `hash`，不一致抛 `MapVersionMismatch`；缺 `objects` 图层报“地图缺少出生点”并回退默认图。26×26 地图加载 <200 ms。

**FR-06 编辑器与校验。** 编辑端用 Tiled 1.12.2，不自研通用编辑器 UI；`mapcheck` 校验连通性、基地砖数、地形比例、出生点路径差、孤立区域、schema 六类规则，输出失败坐标与退出码。5 张错误地图必须全部拦下。

**FR-07 AI 地图生成。** BSP + 约束修复生成候选图，跑 `mapcheck` 通过才输出。每档 30 张、共 90 张 100% 通过，单张 <2 s，同 seed 结果一致。LLM 只做“难度描述 → 参数”和报告解释。

### 3.4 C 对战房间

**FR-08 房间流程。** 创建/加入/离开/准备/匹配，6 类异常各有错误码（`ROOM_NOT_FOUND`、`ROOM_FULL`、`ALREADY_JOINED`、`HOST_LEFT`、`READY_TIMEOUT`、`BAD_PASSWORD`）。重复加入幂等；房主退出按加入顺序移交。

**FR-09 同步与重连。** 20 tick/s 下发 `STATE_SNAPSHOT`，tick 单调；断线带 `lastTick` 重连，30 s 内追平，位置误差 ≤1 格。

**FR-10 观战/回放/解说。** 观战只读，收到 `PLAYER_INPUT` 直接丢弃并记日志；回放存“初始地图 + 事件序列”而不是逐帧快照，回放还原的 `destroyed` 集合与原局 100% 一致；解说可关闭。

### 3.5 D 道具升级

**FR-11 道具。** 落点必须来自 `MapService.freeCells()`，20 张图 × 5 次验证 100% 落在空格；7 类道具；同屏同类上限 3 个；拾取前后地图 `hash` 不变（道具不改地形）。

**FR-12 升级树。** 前置依赖、消耗、效果全部配置化；未满足前置不可点；一条分支 3 级升满。

**FR-13 AI 投放。** 按双方积分差给劣势方补强，单局 ≤3 次，同一方连续 2 次不重复；AI 关闭时按“劣势方每小时 1 次”兜底。

### 3.6 E 大厅战队

**FR-14 大厅。** 登录返回 `token`（2 h）与 `role`；好友增删查；战队上限 20 人；排行榜按 `score` 降序、同分按 `win_rate`；H5 三档宽度无横向滚动。

**FR-15 锦标赛。** 8 人单败生成 7 场无轮空错误；匹配双方胜率差 ≤15%；结果回写后排行榜更新。

### 3.7 个人模块（B-地图系统）需求详述

这一节是本人（姚帅）负责的部分，答辩按这条线讲。

**范围。** FR-05、FR-06、FR-07，加 `NFR-02`。与别人相邻但不越界的地方：A 的三类碰撞判定、C 的广播协议、D 的道具效果、E 的地图摘要展示，我只提供接口和数据，不写别人的实现。

**数据。** 地图元数据字段：`map_id`、`name`、`version`、`seed`、`difficulty`、`hash`、`size{w,h}`、`tiles`、`spawns`。`tiles` 取值是 7 个枚举（`empty`/`brick`/`steel`/`water`/`ice`/`grass`/`base`），`spawns` 是格坐标数组。schema 里 `additionalProperties=false`，临时加字段会被校验器拦下。

**状态。** 地图从草稿到发布走四态：`draft` → `validated` → `published` → `archived`。`draft` 可以随便改；只有 `mapcheck` 全通过才允许进 `validated`；`published` 才能被房间选到；`archived` 保留历史版本，回放要用它的 `hash` 校验。

**接口。** `MapService` 七个方法：`load(mapId, version)`、`isBlocked(rect, mover)`、`terrainAt(cell)`、`hitBullet(cell, power)`、`spawnPoints()`、`freeCells()`、`metadata()`，外加 `TileDestroyed(cell, type, byPlayer)` 事件。调用方分别是 A、C、D、E，签名在 `docs/map-spec.md` §3 冻结在 W11。

**约束。** 26×26 默认、16 px 单格、三层图层、`hash` 规则固定、schema 校验、W11 冻结 v1.0。冰冻/水域/草丛的行为写在图块属性里（`friction`、`cover`、`bullet_pass`），不在代码里写死。

**异常。** schema 校验失败、版本/hash 不一致、出生点到基地无通路、基地周围砖 <6、地形比例越界、`.tmx` 损坏加载失败、出生点被堵。前六类由 `mapcheck` 在发布前拦下，最后一类在对局初始化时拦下并回退默认图。

**验收。** 5 类地形各 1 张截图；每档 30 张 AI 图 100% 通过校验；26×26 加载 <200 ms；AI 生成单张 <2 s；两端 `hash` 一致；5 张错误地图全部被拦下。

## 4. 非功能需求

| 编号 | 类别 | 目标 | 测量方法 | 失败阈值 |
|---|---|---|---|---|
| NFR-01 | 实时性 | 桌面 60 FPS；局域网输入→同步 P95 <100 ms | 帧率叠加；记录 `input_ts` 与 `snapshot_ts` 求差值取 P95 | 连续 30 s <50 FPS 或 P95 >150 ms |
| NFR-02 | 地图性能 | 加载 <200 ms；生成单张 <2 s | 计时脚本 30 次取中位数 | 加载 >300 ms 或生成 >3 s |
| NFR-03 | 并发 | 10 房间 / 50 玩家，错误率 <1% | 5 min 压测（模拟客户端） | 错误率 >3% 或房间状态错乱 |
| NFR-04 | 重连 | 断线 30 s 内恢复且状态一致 | 断网 10 次，记录恢复 tick 与位置误差 | 任一 >45 s 或误差 >2 格 |
| NFR-05 | 兼容性 | Win10/11；Chrome/Edge；H5 320/375/414 | 各 3 组截图 | 任一环境白屏或错位 |
| NFR-06 | 安全 | 服务端权威；`token` 2 h；输入校验；防作弊 | 代码审查 + 12 组越权用例 | 客户端可改血量/积分 |
| NFR-07 | 可维护性 | 单测 ≥60%（地图 ≥70%）；ktlint/detekt 0 error | 本地与 CI 报告 | <50% 或有 error |
| NFR-08 | AI 降级 | AI 不可用时核心玩法不中断 | 断 API 测试 | 断 API 后无法开局或崩溃 |

三处需要说明的取舍：

1. `NFR-01` 的 100 ms 是局域网口径，公网实测到 150~250 ms。答辩只报局域网数据，不混用。
2. `NFR-03` 从 AI 建议的 1000 并发降到 50，理由是我们的部署条件只有一台云主机，压不出 1000 并发，写了也是空指标。
3. `NFR-07` 的地图模块 70% 高于团队 60% 的基线，因为 B 模块的逻辑最独立、最容易写单测，先把这块做扎实。

## 5. 接口需求

### 5.1 WebSocket 消息

| 消息 | 方向 | 字段 | 说明 |
|---|---|---|---|
| `JOIN_ROOM` | C→S | `roomId`、`playerId` | 加入房间 |
| `ROOM_STATE` | S→C | `roomId`、`players`、`state` | 房间状态 |
| `PLAYER_INPUT` | C→S | `tick`、`keys`、`dir` | 输入，20 次/秒 |
| `STATE_SNAPSHOT` | S→C | `tick`、`tanks`、`bullets`、`items` | 状态快照 |
| `MAP_STATE` | S→C | `mapId`、`version`、`hash`、`destroyed` | 地图破坏状态 |
| `ITEM_SPAWN` / `ITEM_PICKUP` | S→C / C→S | `itemId`、`type`、`x`、`y`、`playerId` | 道具 |
| `GAME_OVER` | S→C | `winner`、`stats` | 结算 |
| `RECONNECT` | C→S | `playerId`、`roomId`、`lastTick` | 重连 |

### 5.2 REST 接口

| 接口 | 方法 | 路径 | 入参 | 出参 | 错误码 |
|---|---|---|---|---|---|
| 登录 | POST | `/api/auth/login` | `account`、`password` | `token`、`role` | 401 |
| 房间列表 | GET | `/api/rooms` | `page`、`filter` | 房间列表 | 400 |
| 创建房间 | POST | `/api/rooms` | `mapId`、`maxPlayers` | `roomId` | 400/409 |
| 排行榜 | GET | `/api/ranking` | `season`、`page` | 排行列表 | 400 |
| 回放 | GET | `/api/replays/{id}` | `id` | 事件序列 | 404 |
| 地图元数据 | GET | `/api/maps/{id}` | `id` | `name`/`version`/`hash`/`difficulty` | 404 |

### 5.3 MapService 接口（B 提供）

| 方法 | 返回 | 调用方 | 关键约束 |
|---|---|---|---|
| `load(mapId, version)` | `TileMap` | B/C | 校验 `hash`，不一致抛 `MapVersionMismatch`；结果按 `(mapId, version)` 缓存 |
| `isBlocked(rect, mover)` | `bool` | A | 坦克 AABB 与地形；水域对坦克阻挡、对子弹不阻挡 |
| `terrainAt(cell)` | `TerrainEffect` | A/D | 返回摩擦、遮挡、可通行三属性 |
| `hitBullet(cell, power)` | `BulletHit` | A | 砖 1 发、钢需 `power ≥2`；返回是否破坏与新 `hp` |
| `spawnPoints()` | `List<Cell>` | A/C | 按地图 `objects` 图层返回 |
| `freeCells()` | `List<Cell>` | D | 只返回 `empty` 且未被占用的格 |
| `metadata()` | `MapMetadata` | C/E | 名称、难度、`hash`、尺寸 |

事件 `TileDestroyed(cell, type, byPlayer)`：B 在破坏后立刻抛出，C 转成 `MAP_STATE` 广播，回放把事件按 tick 存起来。

### 5.4 错误响应

统一结构 `{code, message, traceId}`。错误码覆盖 400（参数错）、401（未登录/`token` 过期）、404（对象不存在）、409（状态冲突，如房间满）、503（AI 服务不可用，需降级）。

## 6. 数据需求

完整字段级字典见 `docs/02-DFD.md` §5，这里只列 12 张表与三条一致性约束。

| 表 | 用途 | 关键字段 |
|---|---|---|
| `t_user` | 账号 | `user_id`、`account`、`password_hash`、`role`、`status` |
| `t_player` | 玩家档案 | `player_id`、`user_id`、`nickname`、`team_id`、`status` |
| `t_room` | 房间 | `room_id`、`host_id`、`map_id`、`map_version`、`state`、`max_players` |
| `t_match` | 对局 | `match_id`、`room_id`、`map_id`、`map_hash`、`winner` |
| `t_map` | 地图元数据 | `map_id`、`name`、`version`、`seed`、`difficulty`、`hash`、`size_w`、`size_h`、`state` |
| `t_tile` | 图块 | `map_id`、`x`、`y`、`type`、`hp`、`destructible` |
| `t_item` | 道具 | `item_id`、`type`、`x`、`y`、`respawn_at`、`effect` |
| `t_upgrade` | 升级 | `upgrade_id`、`name`、`level`、`prereq`、`cost`、`effect` |
| `t_team` | 战队 | `team_id`、`name`、`owner_id`、`member_count` |
| `t_ranking` | 排行 | `season_id`、`player_id`、`score`、`win_rate`、`rank` |
| `t_replay` | 回放 | `replay_id`、`match_id`、`map_hash`、`events` |
| `t_log` | 审计日志 | `log_id`、`user_id`、`action`、`target_id`、`at`、`detail` |

一致性约束：

1. 地图字段以 `map.schema.json` 为准，`t_map` 与 `t_tile` 的 `type` 枚举必须与 schema 的 7 值一致。
2. `t_room.map_id`、`t_match.map_id` 都必须能在 `t_map` 找到；`t_match.map_hash` 与当时的 `t_map.hash` 必须相同，否则回放不能校验。
3. `t_replay.events` 只存事件序列加初始地图引用，不存逐帧快照，避免单条记录超过 1 MB。

## 7. 需求追踪矩阵

主干如下，第 2 次课补全测试用例编号与 NFR 的接口级追踪。

| 需求 | 用例 | 类 | 接口 | 测试用例 | 覆盖 |
|---|---|---|---|---|---|
| FR-01 | UC-04 | Tank、Map | `isBlocked`/`terrainAt` | TC-01 八方向移动 | ✅ |
| FR-02 | UC-04 | Bullet、Tank | `hitBullet` | TC-02 三类碰撞 | ✅ |
| FR-03 | UC-04 | Weapon、Bullet | — | TC-03 三类武器 | ✅ |
| FR-04 | UC-04 | Tank、Weapon | AI 瞄准 | TC-04 命中率 | ✅ |
| FR-05 | UC-09 | Map、Tile | `load`/`metadata` | TC-05 五地形加载 | ✅ |
| FR-06 | UC-10 | Map、MapValidator | `mapcheck` | TC-06 校验规则 | ✅ |
| FR-07 | UC-10 | MapGenerator | `generate` | TC-07 30 张/档 | ✅ |
| FR-08 | UC-02/03 | Room、Player | `/api/rooms` | TC-08 房间异常 | ✅ |
| FR-09 | UC-03/04 | Room、Match | `STATE_SNAPSHOT` | TC-09 断线重连 | ✅ |
| FR-10 | UC-07/08 | Replay、AICommentary | `/api/replays` | TC-10 回放还原 | ✅ |
| FR-11 | UC-05 | Item、Tank | `ITEM_SPAWN`/`PICKUP` | TC-11 道具效果 | ✅ |
| FR-12 | UC-06 | Upgrade | — | TC-12 升级树 | ✅ |
| FR-13 | UC-06 | Item、AI | — | TC-13 劣势补强 | ✅ |
| FR-14 | UC-01/11 | User、Team、Ranking | `/api/auth`、`/api/ranking` | TC-14 登录/战队/排行 | ✅ |
| FR-15 | UC-12 | Ranking、Match | `/api/tournament` | TC-15 锦标赛匹配 | ✅ |
| NFR-01 | — | Room、Tank | `STATE_SNAPSHOT` | 待补（第 2 次课） | 部分 |
| NFR-02 | UC-09 | Map | `load`/`generate` | 待补 | 部分 |
| NFR-03~08 | — | — | — | 待补 | 缺口 |

缺口说明：8 条 NFR 里只有 NFR-01、NFR-02 追到了类与接口，其余 6 条要等第 2 次课做完非功能量化和压测方案才能落到测试用例上。这是有意留的缺口，不是漏写。

## 8. 术语、变更与待办

### 8.1 术语表

见 1.3 节，第 2 次课补充界面术语（房间状态、道具名称的中英文对照）。

### 8.2 变更记录

| 日期 | 变更 | 原因 | 影响 |
|---|---|---|---|
| 2026-11-07 | 建立 v0.1 | 实验二第 1 次课 | 需求基线草案 |

### 8.3 初稿待办

- [x] 玩家访谈 3 人（匿名），纪要落 `docs/02-调研记录.md` §3（2026-11-06~07 完成，样本 3 人）；
- [x] 竞品 3 款实测打分 + 截图，落 `docs/02-调研记录.md` §4（2026-11-05~07 完成）；
- [ ] 非功能需求补测量脚本，第 2 次课完成；
- [ ] 追踪矩阵补 NFR 行，第 2 次课完成；
- [ ] 组内评审一次并记录问题，第 2 次课完成。
