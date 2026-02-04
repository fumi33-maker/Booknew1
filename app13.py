import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

st.set_page_config(page_title="本のリサーチリスト (閲覧用)", layout="centered")
st.title("📚 本のリサーチリスト")
st.info("※データの追加・編集はスプレッドシート本体で行ってください。")

# .envからURLを取得
url = os.getenv("SPREADSHEET_URL")

# --- Google Sheetsへの接続設定 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# データの読み込み（10分ごとに更新されるように設定）
df = conn.read(spreadsheet=url, ttl="10m")

# 空の行を削除
df = df.dropna(how="all")

# --- 表示エリア ---
if not df.empty:
    st.subheader("📋 整理されたリスト")
    
    # 「巻」と「ページ」で並び替え（データがある場合のみ）
    # 列名がスプレッドシートの1行目と完全一致している必要があります
    try:
        display_df = df.sort_values(by=["巻", "ページ"]).reset_index(drop=True)
        st.dataframe(display_df, use_container_width=True)
    except KeyError:
        # 万が一列名が違う場合は、そのまま表示
        st.dataframe(df, use_container_width=True)
        st.warning("スプレッドシートの1行目が『巻』『ページ』『内容』になっているか確認してください。")

    # 手動で最新の状態にするボタン
    if st.button("最新の状態に更新"):
        st.cache_data.clear()
        st.rerun()
else:
    st.write("スプレッドシートにデータがありません。")

    