#!/usr/bin/env python3
"""
每日打扫值日播报 → 飞书群机器人
读取 2026_全年打扫安排_周六外包.xlsx,找到今天的值日队伍,推送到飞书 webhook。
用法: python3 notify_cleaning.py [YYYY-MM-DD]   (不传日期则默认今天,按洛杉矶时区)
"""
import sys
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/b301c1ec-f7a7-4856-86ee-a42b99bbea3a"
XLSX = "2026_全年打扫安排_周六外包.xlsx"   # 与脚本同目录,或改成绝对路径

WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def get_today() -> datetime:
    if len(sys.argv) > 1:
        return datetime.strptime(sys.argv[1], "%Y-%m-%d")
    return datetime.now(ZoneInfo("America/Los_Angeles"))


def main() -> None:
    today = get_today()
    date_str = today.strftime("%Y-%m-%d")

    df = pd.read_excel(XLSX)
    df["Date"] = pd.to_datetime(df["Date"])
    row = df[df["Date"].dt.strftime("%Y-%m-%d") == date_str]

    if row.empty:
        print(f"[WARN] {date_str} 不在排班表内,跳过。")
        return

    team = str(row.iloc[0]["Assigned"]).strip()
    weekday_cn = WEEKDAY_CN[today.weekday()]

    if team.lower() == "outsource":
        text = (
            f"🧹 今日打扫值日 | {date_str} {weekday_cn}\n"
            f"今天为【外包清洁】日,各 DSP 无需安排值日。\n"
            f"请保持各自区域基本整洁即可。"
        )
    else:
        text = (
            f"🧹 今日打扫值日 | {date_str} {weekday_cn}\n"
            f"今日值日队伍:【{team}】\n"
            f"请 {team} 小队长安排 1 名司机完成仓库清扫,收工前找前台确认完成度。"
        )

    payload = {"msg_type": "text", "content": {"text": text}}
    req = urllib.request.Request(
        WEBHOOK,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"[OK] Sent for {date_str} → {team}. Feishu response: {resp.read().decode()}")


if __name__ == "__main__":
    main()
