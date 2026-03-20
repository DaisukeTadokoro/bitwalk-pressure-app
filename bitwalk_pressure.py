# bitwalk_pressure.py
# ローカルCLI気圧アプリ v0.1

import requests
import datetime
import sys

# 固定位置（Uji, Kyoto）
LAT = 34.8844
LON = 135.7996
API_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=pressure_msl&timezone=Asia%2FTokyo"

# ゆらぎ指数を定義（気圧差の最大値と変化速度から計算）
def compute_bitwalk_index(pressures):
    if len(pressures) < 2:
        return 0.0
    diffs = [abs(pressures[i+1] - pressures[i]) for i in range(len(pressures)-1)]
    max_diff = max(diffs)
    avg_diff = sum(diffs) / len(diffs)
    return round((max_diff + avg_diff) / 2, 2)

# 実行
if __name__ == "__main__":
    print("[Bitwalk Pressure構文 - 宇治, Kyoto]")
    try:
        r = requests.get(API_URL)
        data = r.json()
        hours = data['hourly']['time'][:12]
        pressures = data['hourly']['pressure_msl'][:12]

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        print(f"現在時刻: {now}\n")

        for h, p in zip(hours, pressures):
            h_disp = h.replace('T', ' ')
            print(f"{h_disp}  →  {p} hPa")

        index = compute_bitwalk_index(pressures)
        print("\n[bitwalkゆらぎ指数]：", index)

        if index < 0.5:
            print("→ 安定構文：強結合の日")
        elif index < 1.5:
            print("→ 中程度のゆらぎ：自然文化に適した日")
        else:
            print("→ 高ゆらぎ構文：保留と余白を大切に")

    except Exception as e:
        print("エラー：", e)
