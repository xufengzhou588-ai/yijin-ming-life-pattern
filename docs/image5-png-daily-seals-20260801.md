# v116 每日灵印替换为图五 PNG 成品图

时间：2026-08-01

本次根据用户指定的参考图，改为直接使用第 5 排“玻璃灵牌”效果图。

已完成：

- 从参考合图中裁出 5 个独立 PNG 素材：
  - `/assets/daily-seals/image5/focus-image5.png`
  - `/assets/daily-seals/image5/spark-image5.png`
  - `/assets/daily-seals/image5/ground-image5.png`
  - `/assets/daily-seals/image5/connect-image5.png`
  - `/assets/daily-seals/image5/restore-image5.png`
- 每日灵印主按钮不再使用内联 SVG，而是直接加载上述 PNG。
- 去掉外层多余玻璃图标壳，避免和图片自带的玻璃牌效果叠加。
- 7 日灵印记录也复用同一套小图缩略显示。
- 版本号升级为 `v116`。

测试入口：

- `http://127.0.0.1:8787/app?v=116`
