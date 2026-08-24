# v120 每日灵印动画源切换为 WebP

时间：2026-08-08

背景：

- v118/v119 已经生成并接入真实 GIF 动画。
- 帧检查确认 5 个 GIF 均有动画变化。
- 但 GIF 对玻璃灵牌的半透明边缘支持较差，容易出现黑边/脏边。

本次调整：

- 保留 GIF 文件作为备份素材。
- 新增 animated WebP 动画素材：
  - `/assets/daily-seals/image5-webp/focus-image5-animated.webp`
  - `/assets/daily-seals/image5-webp/spark-image5-animated.webp`
  - `/assets/daily-seals/image5-webp/ground-image5-animated.webp`
  - `/assets/daily-seals/image5-webp/connect-image5-animated.webp`
  - `/assets/daily-seals/image5-webp/restore-image5-animated.webp`
- 页面主动画源从 GIF 切换为 WebP。
- 系统开启 `prefers-reduced-motion: reduce` 时仍回退静态 PNG。
- 7 日历史小章继续使用静态 PNG，避免页面过度动态。
- 版本号升级为 `v120`。

体积：

- WebP 约 48–67KB/张。
- GIF 约 198–271KB/张。
- APNG 约 713KB–1MB/张，未作为前端默认源。

结论：

- GIF 已经验证能动，但 WebP 更适合最终产品：更干净、更小、更适合玻璃透明边缘。

测试入口：

- `http://127.0.0.1:8787/app?v=120`
