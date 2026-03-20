import streamlit as st
import requests
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- APIキーとエンドポイント ---
API_KEY = "252ba1dc2da2fddea45402047695238f"  # ←あなたのAPIキーに置き換えて
API_URL = "https://api.openweathermap.org/data/3.0/onecall"

st.title("☁️ ピンポイント雨予報")

# --- ユーザー入力 ---
loc = get_geolocation()
st.write("🔍 get_geolocation() の結果:", loc)

if loc and "coords" in loc:
    coords = loc["coords"]
    if "latitude" in coords and "longitude" in coords:
        lat = coords["latitude"]
        lon = coords["longitude"]

        st.write(f"📍 現在地: 緯度 {lat}, 経度 {lon}")


        if st.button("現在の雨予測を取得"):
        # --- リクエスト ---
            params = {
                "lat": lat,
                "lon": lon,
                "appid": API_KEY,
                "units": "metric",
                "lang": "ja"
            }

        # （ここに requests.get() などの処理を続ける)

            res = requests.get(API_URL, params=params)
            if res.status_code == 200:
                data = res.json()
                next_forecasts = data["hourly"][:6]  # 3時間先まで確認


                for entry in next_forecasts:
                    dt = datetime.fromtimestamp(entry["dt"]).strftime("%m/%d %H:%M")
                    weather = entry["weather"][0]["description"]
                    rain = entry.get("rain", {}).get("3h", 0)
                    st.write(f"🕒 {dt}：{weather}（雨量: {rain} mm）")
                    if rain > 0:
                        st.warning("☔ 雨が降る可能性があります！")
            else:
                st.error("API取得に失敗しました。")

else:
    st.warning("位置情報の取得を許可してください。")

