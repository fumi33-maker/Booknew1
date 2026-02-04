import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="My Book Research", page_icon="📖", layout="wide")

# --- 文字を小さくするためのCSS（追加） ---
st.markdown("""
    <style>
    html, body, [class*="st-"] {
        font-size: 14px; /* 全体の文字サイズを少し小さく */
    }
    </style>
    """, unsafe_allow_html=True)

# --- パスワード認証機能（省略せずそのまま） ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True
    st.title("🔒 認証が必要です")
    pwd = st.text_input("合言葉を入力してください", type="password")
    if st.button("ログイン"):
        if pwd == os.getenv("APP_PASSWORD"):
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("合言葉が違います。")
    return False

if check_password():
    st.title("📖 本のリサーチ・コレクション")

    url = os.getenv("SPREADSHEET_URL")
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="5m", encoding="utf-8")
    df = df.dropna(how="all")

    if not df.empty:
        # 1. 検索機能
        search_query = st.text_input("🔍 キーワード検索", "")
        if search_query:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        # 2. 統計
        st.metric(label="リサーチ総数", value=f"{len(df)} 件")
        
        # 3. 表の表示（ここを強化！）
        st.subheader("📋 リサーチリスト")
        
        try:
            display_df = df.sort_values(by=["巻", "ページ"]).reset_index(drop=True)
            
            # st.dataframeの中で列の幅（column_config）を設定します
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "内容": st.column_config.TextColumn(
                        "内容",
                        width="large", # 「内容」欄を広くする（small, medium, largeで指定可）
                    ),
                    "巻": st.column_config.NumberColumn(width="small"),
                    "ページ": st.column_config.NumberColumn(width="small"),
                },
                hide_index=True, # 左端のインデックス（0,1,2...）を隠してスッキリさせる
            )
        except Exception:
            st.dataframe(df, use_container_width=True)

        if st.sidebar.button("🔄 データを最新にする"):
            st.cache_data.clear()
            st.rerun()
            
