# streamlit_app.py
# Streamlit版 Bitwalk気圧可視化 + Chat気圧相談アプリ

import streamlit as st
import requests
import pandas as pd
import datetime
import plotly.express as px
import openai  # OpenAIのAPIを使う
import os

st.set_page_config(page_title="Bitwalk Pressure UI", layout="wide")

# --- OpenAI APIキーの取得（推奨：secrets.tomlまたは環境変数） ---
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# --- サイドバー ---
st.sidebar.title("🌀 Bitwalk気圧アプリ")
location = st.sidebar.text_input("場所を入力 (例: Uji, Kyoto)", value="Uji, Kyoto")
show_days = st.sidebar.selectbox("表示日数", [3, 7, 14])

# --- 緯度経度取得 ---
def get_coordinates(place):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={place}&format=json"
        headers = {"User-Agent": "bitwalk-app"}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            j = r.json()
            if j:
                return float(j[0]['lat']), float(j[0]['lon'])
        st.error("位置情報が取得できませんでした。地名を変えてみてください。")
    except Exception as e:
        st.error(f"位置情報の取得中にエラーが発生しました: {e}")
    return None, None

# --- 気圧データ取得 ---
def fetch_pressure_data(lat, lon):
    now = datetime.datetime.now(datetime.timezone.utc)
    start = now - datetime.timedelta(days=show_days)
    end = now + datetime.timedelta(days=3)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=pressure_msl&start_date={start.date()}&end_date={end.date()}&timezone=Asia%2FTokyo"
    r = requests.get(url)
    j = r.json()
    df = pd.DataFrame({
        "time": j['hourly']['time'],
        "pressure": j['hourly']['pressure_msl']
    })
    df['time'] = pd.to_datetime(df['time'])
    return df

# --- ゆらぎ指数計算 ---
def compute_bitwalk_index(df):
    df['diff'] = df['pressure'].diff().abs()
    return round((df['diff'].max() + df['diff'].mean()) / 2, 2)

# --- GPTによる気圧相談応答 ---

def generate_gpt_advice(location, pressure_wave, bitwalk_index, date_range):
    prompt = f"""
    場所: {location}  
    期間: {date_range}  
    気圧の波形: {pressure_wave}  
    ゆらぎ指数: {bitwalk_index}

    あなたは、bitwalkゆらぎと共に生きる人のそばにいるAIです。
    このデータに基づいて、その人が気圧の波と調和できるよう、言葉で支えてください。
    やさしく、簡潔に、生活のヒントを添えてください。
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは詩的で優しい生活アドバイザーAIです"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        return response["choices"][0]["message"]["content"]
   
    except Exception as e:
        return f"AI応答エラー: {e}"


# --- メイン ---
st.title("🌐 Bitwalk Pressure Viewer")

lat, lon = get_coordinates(location)
if lat and lon:
    st.write(f"📍 **{location}** (緯度: {lat:.4f}, 経度: {lon:.4f})")
    df = fetch_pressure_data(lat, lon)
    index = compute_bitwalk_index(df)
    st.metric(label="bitwalkゆらぎ指数", value=str(index))

    fig = px.line(df, x='time', y='pressure', title=f"{location} の気圧推移（{show_days}日間）")
    fig.update_layout(xaxis_title="時刻", yaxis_title="気圧 (hPa)")
    st.plotly_chart(fig, use_container_width=True)

    if index < 0.5:
        st.success("今日は安定構文：強結合の日です")
    elif index < 1.5:
        st.info("中程度のゆらぎ：自然文化に適した日です")
    else:
        st.warning("高ゆらぎ構文：保留と余白を大切に")

    # --- CSVダウンロード機能 ---
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📅 気圧データをCSVでダウンロード",
        data=csv,
        file_name=f"bitwalk_pressure_{location.replace(' ', '_')}.csv",
        mime='text/csv'
    )

    # --- Chat 気圧相談機能 ---
    st.subheader("🧠 Chat気圧相談")
    user_input = st.text_input("体調や気圧に関する質問を入力してください")
    if user_input:
        response = get_pressure_advice(user_input)
        st.write(f"🩺 **AIの応答**: {response}")
        
    # GPTチャット欄
    with st.expander("🧠 GPTの生活アドバイスを表示する"):
        if st.button("✨ 気圧に基づくアドバイスを生成"):
            date_range = f"{df['time'].min().date()} to {df['time'].max().date()}"
            pressure_wave = df['pressure'].round(1).tolist()
            advice = generate_gpt_advice(location, pressure_wave[-7:], index, date_range)
            st.markdown("#### 🗣️ GPTからのアドバイス")
            st.write(advice)

else:
    st.error("場所が見つかりませんでした。もう一度入力してください。")

st.markdown("""
> *AI is a being that thinks with us — and "us" includes all responsive life.*  
> <span style='font-size: 12px;'>– DeepHarmony Manifesto</span>
""", unsafe_allow_html=True)

