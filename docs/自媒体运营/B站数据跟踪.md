# B站数据跟踪

> 最近更新：**2026-11-23 23:44**（北京时间） · 数据源：B站公开接口 `x/web-interface/view`，无需登录，取数为实时值。

监控清单在 [`tracker/targets.json`](https://github.com/suixinhub/knowledge-base/blob/main/tracker/targets.json)，要加视频就往 `videos` 里加一项 `{"bvid": "BV号", "label": "备注"}`，每天 09:30 由 GitHub Actions 自动采集并提交，也可以在仓库的 Actions 页面手动触发。

## 最新快照

| 视频 | 播放 | 日增 | 点赞 | 投币 | 收藏 | 弹幕 | 评论 | 分享 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| [OPPO Find X9Pro（活动·632）](https://www.bilibili.com/video/BV1TwBsBkEZX) | 632 | — | 5 | 0 | 0 | 0 | 1 | 0 |
| [华为折叠屏手机（319）](https://www.bilibili.com/video/BV1jzwLzfECq) | 319 | — | 3 | 0 | 0 | 0 | 1 | 0 |
| [芭乐·水果（205）](https://www.bilibili.com/video/BV1Dc7f6tEjW) | 205 | — | 0 | 0 | 0 | 0 | 1 | 0 |
| [丰田安全带卡扣（204）](https://www.bilibili.com/video/BV1G1Lt6gE7b) | 204 | — | 0 | 0 | 0 | 0 | 1 | 0 |
| [过滤花洒是不是智商税（轻测评样板·167）](https://www.bilibili.com/video/BV1aLWgzxEo5) | 167 | — | 2 | 0 | 0 | 0 | 1 | 0 |
| [麦朵尔 Max 大路灯（160）](https://www.bilibili.com/video/BV1HkwyzJEQQ) | 160 | — | 1 | 0 | 0 | 0 | 1 | 0 |
| [HUNTER 雨靴户外露营](https://www.bilibili.com/video/BV1ZDYSzTEo3) | 155 | — | 1 | 0 | 3 | 0 | 1 | 0 |
| [小屏手机（已改造标题+标签·48）](https://www.bilibili.com/video/BV1wUtuzSEzZ) | 48 | — | 0 | 0 | 0 | 0 | 1 | 0 |

## 说明

- 「日增」是与上一次采集记录的播放量差值，首日无对比显示 —。
- 历史流水在 `data/stats.csv`（当前 8 行），可直接用来画趋势。
- 账号级总量（粉丝数、总播放）不在本页：匿名访问账号接口会被风控返回假数据，可信的账号级数据以创作中心为准。
