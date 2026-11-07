# 坦克大战·联机复刻 实验二 DFD 与数据字典

> 组别：cs24104 / 计科 242　组长：姚帅（2024210622）　版本：v0.1（实验二第 1 次课）
> 日期：2026-11-07　图件：`docs/model/lab2/`（Enterprise Architect 17.2 绘制并导出）

本文件记录实验二的 DFD 分层结果和字段级数据字典。四张图都在 `model/TankBattle.qea` 的 `02 实验二 需求分析 / 01 DFD` 包下，用 Data Flow Diagram 图类型绘制：外部实体用矩形、加工用圆角矩形并带编号、数据存储用左侧开口矩形、数据流用带名字的箭头。加工编号一旦定下就不再改，后面 SRS、顺序图、追踪矩阵都用同一套编号。

## 1. DFD 顶层图（fig2-2-dfd-top.png）

顶层图把整个系统看成一个加工 0「坦克大战联机系统」，只画外部实体和进出系统的数据流。

| 外部实体 | 与系统的数据流 | 说明 |
|---|---|---|
| 玩家 | 登录账号 / `token`+角色；房间条件 / 房间号+队伍；按键输入 / 状态快照 | 桌面端与 H5 两个入口都算玩家 |
| 观战者 | 观战请求 / 状态流 | 只读，不发输入 |
| 管理员 | 地图管理 / 校验结果；举报处理 / 处理结果 | 通过后台页进入 |
| AI 服务 | 解说请求 / 解说文本；生成参数 / 候选地图；瞄准请求 / 射击角 | 外部大模型/算法服务，可降级 |

图 T-1（`fig2-2-dfd-top.png`）说明：系统对外只有 4 个交互对象，内部 6 个加工在 0 层展开。顶层的每一条流在 0 层都能找到对应的入口或出口，没有悬空流；外部实体不直接连数据存储，玩家要写数据必须经过 P1 或 P2。

## 2. DFD 0 层图（fig2-3-dfd-0.png）

0 层把顶层加工拆成 6 个加工和 6 个数据存储。

### 2.1 加工

| 加工 | 名称 | 输入 | 输出 | 读/写存储 |
|---|---|---|---|---|
| P1 | 登录与大厅 | 账号/token 请求、好友与战队操作 | `token`、角色、好友列表 | D1 用户库 |
| P2 | 房间匹配 | 房间条件、玩家 id | 房间号、队伍、开局事件 | D2 房间库 |
| P3 | 战斗引擎 | 按键输入、地形查询结果、道具效果 | 状态快照、命中/死亡事件、对局结果 | D3 对局库 |
| P4 | 地图服务 | `map_id`/`version`、图块、子弹命中 | 地形查询结果、破坏事件、出生点 | D4 地图库 |
| P5 | 道具升级 | 战局数据、拾取事件、升级选择 | 道具事件、属性变化 | D5 道具配置 |
| P6 | 排行/锦标赛 | 对局结果、赛季报名 | 积分、排名、对阵表 | D6 排行榜 |

### 2.2 数据流

| 编号 | 流 | 起点 → 终点 | 内容 |
|---|---|---|---|
| F1 | 登录账号 / token+角色 | 玩家 ↔ P1 | 账号、密码、`token`、角色 |
| F2 | 读写用户 | P1 → D1 | 账号、`password_hash`、`role` |
| F3 | 房间条件 / 房间号+队伍 | 玩家 ↔ P2 | 地图、人数、房间号、玩家列表 |
| F4 | 读写房间 | P2 → D2 | `room_id`、`state`、`max_players` |
| F5 | 开局 | P2 → P3 | 对局 id、地图版本、初始状态 |
| F6 | 地形查询 / 命中结果 | P3 ↔ P4 | `isBlocked`、`terrainAt`、`hitBullet` 的入参与返回 |
| F7 | 读地图 | P4 → D4 | `map_id`、`version`、`tiles` |
| F8 | 拾取结算 / 属性变化 | P3 ↔ P5 | 拾取事件、攻击/速度/护甲变化 |
| F9 | 读道具配置 | P5 → D5 | 道具类型、效果、冷却 |
| F10 | 写对局 | P3 → D3 | `match_id`、起止时间、胜负 |
| F11 | 对局结果 | P3 → P6 | 胜负、击杀数、用时 |
| F12 | 写排行 | P6 → D6 | 赛季、积分、胜率 |
| F13 | 积分/排名 | P6 → 玩家 | 积分变化、名次 |
| F14 | 观战请求 / 状态流 | 观战者 ↔ P3 | 观战订阅、只读快照 |
| F15 | 地图管理 / 校验结果 | 管理员 ↔ P4 | 上传、校验报告、发布状态 |
| F16 | 解说请求 / 解说文本 | P3 ↔ AI 服务 | 对局事件、解说句子 |

图 T-2（`fig2-3-dfd-0.png`）说明：每个加工至少 1 入 1 出，每个存储至少被读或写一次（D1~D6 的读写流在图上是 F2、F4、F7、F9、F10、F12）。P3 是流量最大的加工，它同时连 P4、P5、P6、D3、观战者和 AI 服务，1 层图因此把 P3 和 P4 各展开一次，而不是把六个加工全展开。

### 2.3 平衡检查

- 顶层 4 条外部流（玩家、观战者、管理员、AI）在 0 层都有落点：玩家→F1/F3/F13，观战者→F14，管理员→F15，AI→F16。
- 0 层没有新增外部实体，也没有出现顶层没有的外部流。
- 数据存储只在 0 层出现，顶层不画存储，符合分层要求。

## 3. DFD 1 层图之一：P3 战斗引擎（fig2-4-dfd-1-battle.png）

P3 拆成 5 个子加工。跨图引用的 P4、P5、C 房间服务用带「跨图引用」标注的方框表示，避免 1 层图重复画别层的元素。

| 子加工 | 名称 | 输入 | 输出 |
|---|---|---|---|
| P3.1 | 输入处理 | 按键/触屏、`tick` | 移动指令、射击指令（带 `tick`） |
| P3.2 | 移动与地形碰撞 | 移动指令、地形查询结果 | 新坐标、朝向、碰撞结果 |
| P3.3 | 射击与弹道 | 射击指令、武器参数、命中结果 | 子弹状态、`hitBullet` 调用 |
| P3.4 | 伤害/死亡/复活 | 命中事件、道具效果 | 生命值变化、死亡/复活事件、胜负 |
| P3.5 | 状态广播 | 本 tick 全部状态 | `STATE_SNAPSHOT(tick)` |

关键流：

| 流 | 起点 → 终点 | 内容 |
|---|---|---|
| 按键/触屏 | 玩家 → P3.1 | 8 方向输入、开火键 |
| 移动指令 | P3.1 → P3.2 | `dx`、`dy`、`dir`、`tick` |
| `isBlocked/terrainAt` | P3.2 → P4（跨图） | `rect`、`mover`、`cell` |
| 射击指令 | P3.1 → P3.3 | 方向、武器 id |
| `hitBullet(cell, power)` | P3.3 → P4（跨图） | 命中格、威力 |
| 命中/伤害 | P3.3 → P3.4 | 被击中的坦克、扣血量 |
| 死亡/复活事件 | P3.4 → P3.5 | 死亡方、复活时间 |
| 道具效果 | P5（跨图）→ P3.4 | 攻击/护甲/速度增量 |
| `STATE_SNAPSHOT` | P3.5 → C 房间服务（跨图） | `tick`、tanks、bullets、items |
| 写对局事件 | P3.4 → D3 | 击杀、破坏、结算 |
| 道具配置 | D5 → P5（跨图） | 道具效果表 |

图 T-3（`fig2-4-dfd-1-battle.png`）说明：1 层只展开 P3，P4/P5/C 用跨图引用框，箭头方向就是调用方向——P3.2 向 P4 要地形结果，P3.3 向 P4 报子弹命中；P4 反过来把破坏结果交给 C 广播（见 4.1 的图）。P3.4 是所有伤害与生死的唯一入口，A 模块的“三类碰撞”判定结果都汇总到这里，避免 P3.3 和 P3.2 各写一套扣血逻辑。

## 4. DFD 1 层图之二：P4 地图服务（fig2-4b-dfd-1-map.png）

P4 拆成 4 个子加工。调用方 A 战斗引擎和 C 房间服务同样用跨图引用框。

| 子加工 | 名称 | 输入 | 输出 |
|---|---|---|---|
| P4.1 | 地图加载 | `map_id`、`version`、`hash` | `TileMap`、`MapMetadata` |
| P4.2 | 地形查询 | `rect`、`cell` | `isBlocked` 布尔、`TerrainEffect` |
| P4.3 | 子弹命中 | `hitBullet(cell, power)` | `BulletHit`（是否破坏）、`TileDestroyed` |
| P4.4 | 出生点/空位 | 地图版本、已占用格 | `spawnPoints()`、`freeCells()` |

关键流：

| 流 | 起点 → 终点 | 内容 |
|---|---|---|
| `map_id`/`version` | C/客户端 → P4.1 | 加载请求 |
| 读地图数据 | P4.1 → D4 | `.tmx` 内容、`tiles`、`hash` |
| `TileMap` | P4.1 → P4.2 | 内存中的地形格与属性 |
| `isBlocked`/`terrainAt` | P4.2 → A（跨图） | 可通行、摩擦、遮挡 |
| `hitBullet(cell, power)` | A（跨图）→ P4.3 | 命中格、威力 |
| `TileDestroyed` | P4.3 → C（跨图） | 被破坏格、图块类型、破坏者 |
| 写破坏事件 | P4.3 → D3 | 破坏记录（回放用） |
| 出生点/空位 | P4.4 → A（跨图） | 出生点列表、空格列表 |
| 读地图元数据 | P4.4 → D4 | 尺寸、出生点坐标 |

图 T-4（`fig2-4b-dfd-1-map.png`）说明：P4 对外只有三个查询入口（地形、命中、出生点）和一条加载入口，查询都是同步返回，只有破坏事件往外推。D4 是只读为主的地图库，只有管理员发布地图时写；D3 只在 P4.3 写破坏事件，供 C 做 `MAP_STATE` 和回放。

## 5. 数据字典

字段类型按 `map.schema.json` 和数据库设计统一：`string` / `int` / `bool` / `enum` / `array` / `datetime`。`*` 表示必填。

### 5.1 t_user 用户

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `user_id` | string | PK，`^u_[0-9a-f]{8}$` | 用户唯一标识 |
| `account` | string | 唯一，4~20 字符，`[a-zA-Z0-9_]` | 登录名 |
| `password_hash` | string | 非空，60 字符 | bcrypt 哈希，不存明文 |
| `role` | enum | `player` / `admin` | 角色，决定后台权限 |
| `status` | enum | `active` / `banned` | 封禁后拒绝登录 |
| `created_at` | datetime | 非空 | 注册时间 |

### 5.2 t_player 玩家档案

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `player_id` | string | PK，`^p_[0-9a-f]{8}$` | 玩家标识 |
| `user_id` | string | FK → `t_user.user_id`，唯一 | 一个账号一个档案 |
| `nickname` | string | 2~12 字符 | 显示名 |
| `team_id` | string | FK → `t_team.team_id`，可空 | 所属战队 |
| `status` | enum | `idle` / `in_room` / `in_match` / `offline` | 在线状态 |
| `last_login` | datetime | 可空 | 最后登录时间 |

### 5.3 t_room 房间

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `room_id` | string | PK，`^r_[0-9a-f]{6}$` | 房间号 |
| `host_id` | string | FK → `t_player.player_id` | 房主 |
| `map_id` | string | FK → `t_map.map_id` | 选用地图 |
| `map_version` | int | ≥1 | 地图版本，开局时比对 |
| `state` | enum | `waiting` / `ready` / `playing` / `finished` / `closed` | 房间状态机 |
| `max_players` | int | 2~8 | 人数上限 |
| `password` | string | 可空，≤8 字符 | 房间密码 |
| `created_at` | datetime | 非空 | 创建时间 |

### 5.4 t_match 对局

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `match_id` | string | PK，`^m_[0-9a-f]{8}$` | 对局标识 |
| `room_id` | string | FK → `t_room.room_id` | 所属房间 |
| `map_id` | string | FK → `t_map.map_id` | 实际使用地图 |
| `map_hash` | string | 16 字符 | 开局时两端比对 |
| `started_at` | datetime | 非空 | 开始时间 |
| `ended_at` | datetime | 可空 | 结束时间 |
| `winner` | enum | `red` / `blue` / `draw` / `abort` | 胜负；`abort` 表示中途流产 |

### 5.5 t_map 地图元数据

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `map_id` | string | PK，`^[a-z0-9_]{3,20}$` | 如 `arena_01` |
| `name` | string | 非空，≤20 字符 | 显示名 |
| `version` | int | ≥1 | 联机比对 |
| `seed` | int | ≥0 | 生成种子；手工图为 0 |
| `difficulty` | enum | `easy` / `normal` / `hard` | 难度 |
| `hash` | string | 8~64 字符 | 规范化 JSON 的 SHA-256 前 16 位 |
| `size_w` | int | 13~52，默认 26 | 宽（格） |
| `size_h` | int | 13~52，默认 26 | 高（格） |
| `state` | enum | `draft` / `validated` / `published` / `archived` | 发布状态 |
| `owner_id` | string | FK → `t_player.player_id` | 作者 |

### 5.6 t_tile 图块

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `map_id` | string | PK 之一，FK → `t_map.map_id` | 所属地图 |
| `x` | int | 0~25 | 列 |
| `y` | int | 0~25 | 行 |
| `type` | enum | `empty`/`brick`/`steel`/`water`/`ice`/`grass`/`base` | 图块类型 |
| `hp` | int | ≥0 | 砖 1、钢 2、其他 0 |
| `destructible` | bool | 非空 | 是否可破坏 |

### 5.7 t_item 道具

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `item_id` | string | PK，`^i_[0-9a-f]{6}$` | 道具实例 |
| `type` | enum | `repair`/`shield`/`speed`/`power`/`rapid`/`freeze`/`bomb` | 道具类型 |
| `x` | int | ≥0 | 落点列 |
| `y` | int | ≥0 | 落点行 |
| `respawn_at` | datetime | 可空 | 下次刷新时间 |
| `effect` | string | JSON | 效果参数（时长、倍率） |

### 5.8 t_upgrade 升级

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `upgrade_id` | string | PK | 升级项 |
| `name` | string | 非空 | 显示名 |
| `level` | int | 1~3 | 等级 |
| `prereq` | string | 可空 | 前置升级 id |
| `cost` | int | ≥0 | 积分消耗 |
| `effect` | string | JSON | 属性增益 |

### 5.9 t_team 战队

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `team_id` | string | PK，`^t_[0-9a-f]{6}$` | 战队标识 |
| `name` | string | 唯一，2~12 字符 | 战队名 |
| `owner_id` | string | FK → `t_player.player_id` | 队长 |
| `member_count` | int | 1~20 | 成员数，超限拒绝 |
| `created_at` | datetime | 非空 | 创建时间 |

### 5.10 t_ranking 排行

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `season_id` | string | PK 之一 | 赛季 |
| `player_id` | string | PK 之一，FK | 玩家 |
| `score` | int | ≥0 | 积分 |
| `win_rate` | float | 0~1 | 胜率 |
| `rank` | int | ≥1 | 名次，按 score 降序、同分按 win_rate |

### 5.11 t_replay 回放

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `replay_id` | string | PK | 回放标识 |
| `match_id` | string | FK → `t_match.match_id`，唯一 | 一局一份 |
| `map_hash` | string | 16 字符 | 回放校验用 |
| `events` | array | JSON 数组 | 初始地图 + 事件序列，不存逐帧快照 |
| `created_at` | datetime | 非空 | 生成时间 |

### 5.12 t_log 审计日志

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `log_id` | string | PK | 日志标识 |
| `user_id` | string | FK，可空 | 操作人；系统动作可空 |
| `action` | string | ≤32 字符 | 如 `MAP_PUBLISH`、`ROOM_CLOSE` |
| `target_id` | string | 可空 | 被操作对象 |
| `at` | datetime | 非空 | 时间 |
| `detail` | string | JSON，可空 | 上下文 |

## 6. 与 schema 的一致性

`maps/schema/map.schema.json` 里 `additionalProperties=false`，所以 `t_map` 的字段只能多不能乱加：加字段要同时改 schema、`map-spec.md` 和本文档，走接口变更流程（`docs/协作规范.md` §5）。本文档与 `map-spec.md` §2 的字段名逐字对齐，没有出现 `mapId` 和 `map_id` 两种写法混用。

## 7. 变更记录

| 日期 | 变更 | 原因 |
|---|---|---|
| 2026-11-07 | 建立 v0.1：顶层 + 0 层 + 2 张 1 层，数据字典 12 张表 | 实验二第 1 次课 |
