#!/usr/bin/env python3
"""B站视频数据每日采集。

读取 tracker/targets.json 里的 BV 号清单，逐个调用 B站公开接口
（x/web-interface/view，无需登录）取播放/点赞/投币/收藏等数据：

1. 追加一行到 data/stats.csv（长期流水，可画趋势）
2. 与上一次记录比对，算增量
3. 重写 docs/自媒体运营/B站数据跟踪.md（知识库里的快照页）

只用标准库，便于在任何环境（含 GitHub Actions）直接运行。
"""

import csv
import datetime
import json
import os
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = os.path.join(ROOT, "tracker", "targets.json")
CSV_PATH = os.path.join(ROOT, "data", "stats.csv")
PAGE = os.path.join(ROOT, "docs", "自媒体运营", "B站数据跟踪.md")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
FIELDS = ["date", "bvid", "title", "view", "like", "coin", "favorite",
          "danmaku", "reply", "share"]


def now_cn():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))


def fetch(bvid, retries=2):
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", UA)
            req.add_header("Referer", "https://www.bilibili.com/")
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode("utf-8"))
            if d.get("code") == 0:
                s = d["data"]["stat"]
                return {
                    "title": d["data"]["title"],
                    "view": s.get("view", 0), "like": s.get("like", 0),
                    "coin": s.get("coin", 0), "favorite": s.get("favorite", 0),
                    "danmaku": s.get("danmaku", 0), "reply": s.get("reply", 0),
                    "share": s.get("share", 0),
                }
            msg = f"code={d.get('code')} {d.get('message')}"
        except Exception as e:  # 网络类错误，重试
            msg = f"error={e}"
        if attempt < retries:
            time.sleep(3)
    print(f"  [WARN] {bvid}: {msg}")
    return None


def load_history():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return [dict(r) for r in csv.DictReader(f)]


def prev_record(rows, bvid, today):
    """上一次（非今天）的记录，用于算增量。"""
    for r in reversed(rows):
        if r["bvid"] == bvid and r["date"] != today:
            return r
    return None


def fmt_delta(cur, prev, key):
    if prev is None:
        return "—"
    try:
        d = int(cur[key]) - int(prev[key])
    except (ValueError, KeyError):
        return "—"
    return f"+{d}" if d >= 0 else str(d)


def main():
    today = now_cn().strftime("%Y-%m-%d")
    ts = now_cn().strftime("%Y-%m-%d %H:%M")
    cfg = json.load(open(TARGETS, encoding="utf-8"))
    videos = cfg["videos"]
    print(f"[bili-tracker] {ts}  监控 {len(videos)} 条")

    rows = load_history()
    new_rows, snapshot = [], []

    for v in videos:
        bvid = v["bvid"]
        s = fetch(bvid)
        if s is None:
            snapshot.append({"bvid": bvid, "label": v.get("label", ""),
                             "error": True})
            continue
        rec = {"date": today, "bvid": bvid, "title": s["title"],
               **{k: s[k] for k in FIELDS[3:]}}
        rows.append(rec)
        new_rows.append(rec)
        prev = prev_record([r for r in rows if r is not rec], bvid, today)
        snapshot.append({
            "bvid": bvid, "label": v.get("label", ""), "title": s["title"],
            "stats": s, "prev": prev,
        })
        time.sleep(1.5)  # 礼貌限速，避免触发风控

    # 1) 追加 CSV
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    is_new = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            w.writeheader()
        for r in new_rows:
            w.writerow(r)
    print(f"  追加 {len(new_rows)} 行到 data/stats.csv")

    # 2) 生成快照页
    lines = [
        "# B站数据跟踪",
        "",
        f"> 最近更新：**{ts}**（北京时间） · 数据源：B站公开接口 `x/web-interface/view`，无需登录，取数为实时值。",
        "",
        "监控清单在 [`tracker/targets.json`](https://github.com/suixinhub/knowledge-base/blob/main/tracker/targets.json)，"
        "要加视频就往 `videos` 里加一项 `{\"bvid\": \"BV号\", \"label\": \"备注\"}`，"
        "每天 09:30 由 GitHub Actions 自动采集并提交，也可以在仓库的 Actions 页面手动触发。",
        "",
        "## 最新快照",
        "",
        "| 视频 | 播放 | 日增 | 点赞 | 投币 | 收藏 | 弹幕 | 评论 | 分享 |",
        "|---|--:|--:|--:|--:|--:|--:|--:|--:|",
    ]
    ok = [s for s in snapshot if not s.get("error")]
    err = [s for s in snapshot if s.get("error")]
    for s in ok:
        st, p = s["stats"], s["prev"]
        lines.append(
            f"| [{s['label'] or s['title'][:24]}]"
            f"(https://www.bilibili.com/video/{s['bvid']}) "
            f"| {st['view']} | {fmt_delta(st, p, 'view')} "
            f"| {st['like']} | {st['coin']} | {st['favorite']} "
            f"| {st['danmaku']} | {st['reply']} | {st['share']} |")
    if err:
        lines += ["", "## 本次采集失败", ""]
        for s in err:
            lines.append(f"- {s['bvid']}（{s.get('label', '')}）——接口异常，今日无数据")
    lines += [
        "",
        "## 说明",
        "",
        "- 「日增」是与上一次采集记录的播放量差值，首日无对比显示 —。",
        f"- 历史流水在 `data/stats.csv`（当前 {len(rows)} 行），可直接用来画趋势。",
        "- 账号级总量（粉丝数、总播放）不在本页：匿名访问账号接口会被风控返回假数据，"
        "可信的账号级数据以创作中心为准。",
        "",
    ]
    os.makedirs(os.path.dirname(PAGE), exist_ok=True)
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  快照页已更新：docs/自媒体运营/B站数据跟踪.md")


if __name__ == "__main__":
    main()
