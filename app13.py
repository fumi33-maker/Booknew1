import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# ページの設定（少し広く、可愛く）
st.set_page_config(page_title="My Book Research", page_icon="📖", layout="wide")

# タイトル
st.title("📖 本のリサーチ・コレクション")

# --- データ読み込み ---
url = os.getenv("SPREADSHEET_URL")
conn = st.connection("gsheets", type=GSheetsConnection)

# データを読み込んで、空行を削除
df = conn.read(spreadsheet=url, ttl="5m")
df = df.dropna(how="all")

if not df.empty:
    # --- 1. 検索機能エリア ---
    st.subheader("🔍 検索・絞り込み")
    search_query = st.text_input("キーワードを入力してね（巻数や内容など）", "")

    # 検索機能のロジック
    if search_query:
        # すべての列を対象に検索
        df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

    # --- 2. 統計表示（可愛いバルーン風） ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="リサーチ総数", value=f"{len(df)} 件")
    
    # --- 3. 表の表示（見た目を可愛く） ---
    st.subheader("📋 リサーチリスト")
    
    try:
        # 並び替え
        display_df = df.sort_values(by=["巻", "ページ"]).reset_index(drop=True)
        
        # 表のデザインカスタマイズ
        st.dataframe(
            display_df.style.set_properties(**{
                'background-color': '#f0f2f6', # 薄いグレー
                'color': '#31333F',           # 文字色
                'border-color': 'white'
            }).highlight_max(axis=0, subset=['巻'], color='#ffebf0'), # 最大の巻数をピンクに
            use_container_width=True
        )
    except Exception:
        st.dataframe(df, use_container_width=True)

    # --- 4. 更新ボタン（サイドバーに配置してスッキリ） ---
    if st.sidebar.button("🔄 データを最新にする"):
        st.cache_data.clear()
        st.rerun()

else:
    st.info("スプレッドシートにデータがまだありません。入力して待っててね！")

# サイドバーにちょっとしたメッセージ
st.sidebar.markdown("---")
st.sidebar.write("💡 **コツ**")
st.sidebar.caption("スプレッドシートを更新したら、上のボタンを押すとすぐに反映されるよ！")
