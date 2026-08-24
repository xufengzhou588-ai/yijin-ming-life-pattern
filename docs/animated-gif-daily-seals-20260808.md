# v118 每日灵印 GIF 微动画

时间：2026-08-08

目标：在用户确认的“图五第 5 排玻璃灵牌”基础上，让小人/灵牌产生轻微真实动效，增加趣味性，但不做夸张视频化动画。

已完成：

- 新增 5 个真实 GIF 动画素材：
  - `/assets/daily-seals/image5-animated/focus-image5.gif`
  - `/assets/daily-seals/image5-animated/spark-image5.gif`
  - `/assets/daily-seals/image5-animated/ground-image5.gif`
  - `/assets/daily-seals/image5-animated/connect-image5.gif`
  - `/assets/daily-seals/image5-animated/restore-image5.gif`
- 动效设计：
  - 定心：背后光圈呼吸发光。
  - 起势：火焰与火光微微闪动。
  - 安土：地气/石台能量轻微脉动。
  - 结缘：两侧人物区域轻微靠近，中间红结发光。
  - 养源：水波与新芽光点轻微流动。
- 主“每日灵印”按钮和核心画像灵牌使用 GIF。
- 7 日灵印历史仍使用静态 PNG，避免页面过于嘈杂。
- 支持系统 `prefers-reduced-motion: reduce`：用户开启减少动态时自动回退静态 PNG。
- 版本号升级为 `v118`。

实现说明：

- 本轮没有重新生成 AI 图像，而是基于现有图五 PNG 做本地帧动画。
- 每个 GIF 为 192×192，约 198–233KB，适合当前 96px 左右的 UI 显示。

测试入口：

- `http://127.0.0.1:8787/app?v=118`
