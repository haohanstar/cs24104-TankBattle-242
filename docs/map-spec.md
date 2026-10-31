# B-地图系统 规范与接口（v0.1）

> 负责人：姚帅　适用：桌面端（Kotlin + LibGDX）　地图编辑：Tiled 1.12.2
> 状态：实验一初稿；W11 冻结 v1.0

## 1. 地图格式

- 使用 Tiled 正交地图 `.tmx`，26×26 格，单格 16×16 px，画布 416×416 px。
- 图层：
  - `terrain`：砖墙、钢墙、水域、冰面、空地。
  - `decor`：草丛、基地、装饰；草丛在坦克上层绘制。
  - `objects`：出生点、基地、道具候选点。
- 图块属性（Tiled custom properties）：
  - `collision`：`none | block | bullet`
  - `destructible`：`true | false`
  - `hp`：砖墙 1，钢墙 2（需 power≥2 才可破）
  - `bullet_pass`：`true | false`
  - `friction`：冰面 0.02，其他 0.2
  - `cover`：草丛 true（遮挡但不阻挡）
  - `score`：破坏得分

## 2. 地图元数据

| 字段 | 类型 | 说明 |
|---|---|---|
| `map_id` | string | 地图唯一标识，如 `arena_01` |
| `name` | string | 显示名 |
| `version` | int | 地图版本，联机比对 |
| `seed` | int | 生成种子；手工图为 0 |
| `difficulty` | enum | easy / normal / hard |
| `hash` | string | 静态地图规范化 JSON 的 SHA-256 前 16 位 |
| `size` | {w,h} | 26×26 |

## 3. `MapService` 接口

| 方法 | 返回 | 调用方 | 说明 |
|---|---|---|---|
| `load(mapId, version)` | `TileMap` | B / C | 加载并缓存地图 |
| `isBlocked(rect, mover)` | `bool` | A | 坦克 AABB 与地形碰撞 |
| `terrainAt(cell)` | `TerrainEffect` | A / D | 摩擦、遮挡、可通行 |
| `hitBullet(cell, power)` | `BulletHit` | A | 子弹命中；返回是否破坏 |
| `spawnPoints()` | `List<Cell>` | A / C | 出生点 |
| `freeCells()` | `List<Cell>` | D | 可放置道具的空格 |
| `metadata()` | `MapMetadata` | C / E | 地图名/难度/hash |

事件：`TileDestroyed(cell, type, byPlayer)`；C 将其广播为 `MAP_STATE`，回放保存“初始地图 + 事件序列”。

## 4. 碰撞与地形效果

- 坦克使用 AABB，按 X/Y 轴分离移动；每轴移动前查询目标格，避免高速穿透。
- 砖墙：普通子弹 1 发破坏；钢墙：power≥2 才能破坏；水域：坦克不可进入，子弹可过；冰面：降低摩擦、增加滑行；草丛：不阻挡，绘制在坦克上层；基地：不可破坏（被击中判负）。
- 边界：A 负责坦克-坦克、坦克-子弹、武器与弹道；B 只负责坦克/子弹-地形。两边不重复写碰撞循环。

## 5. 地图编辑器（Tiled）

- 编辑端使用 Tiled 1.12.2，不重复开发通用编辑器 UI。
- 工程：`maps/tankbattle.tiled-project`；图块集：`maps/tiles.tsx`；模板：出生点、基地、道具点。
- 自定义属性与图层规范由 `maps/schema/map.schema.json` 校验。
- 游戏内提供“加载 + 预览 + 校验”入口；地图作者在 Tiled 中编辑并保存 `.tmx`。

## 6. AI 地图生成与平衡校验

- 输入：难度、尺寸、seed、主题。
- 生成器：BSP/细胞自动机/模板 + 约束修复；输出 `.tmx`。
- 校验器：
  - 每个出生点到基地存在通路；
  - 基地周围 ≥6 块砖，且出生点到基地无直线通视；
  - 砖 15~30%、钢 5~12%、水 ≤10%、冰 ≤8%、草 5~15%；
  - 出生点路径长度差 ≤15%，掩体比例差 ≤10%；
  - 无面积 >5% 的孤立区域。
- LLM 只做“难度描述 → 生成参数”和校验报告解释；不让模型直接输出瓦片。API 不可用时退回参数表。
- 指标：每档 30 张，修复后 100% 通过；单张 <2s；3 位同学试玩公平性 ≥3.5/5。

## 7. 与其他模块的接口

| 对方 | 他负责 | 我提供 | 我依赖他 |
|---|---|---|---|
| A 战斗引擎 | 坦克/子弹/武器 | `isBlocked`、`terrainAt`、`hitBullet`、出生点 | 战斗循环调用接口；W11 确认签名 |
| C 对战房间 | 房间/同步/观战 | `map_id/version/hash`、`MAP_STATE` 事件 | 下发地图元数据；W12 定协议 |
| D 道具升级 | 道具生成/拾取 | `freeCells()`、道具候选点 | 道具不改变地形；W12 定规则 |
| E 大厅战队 | 大厅/排行 | 地图名、难度、缩略图 | 地图选择/预览 UI；W14 联调 |
