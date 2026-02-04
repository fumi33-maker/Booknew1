import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from dotenv import load_dotenv

# 設定の読み込み
load_dotenv()

# ページの設定
st.set_page_config(page_title="My Private Book Research", page_icon="🔒", layout="wide")

# --- パスワード認証機能 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # ログイン画面
    st.title("🔒 認証が必要です")
    st.write("このリサーチリストは保護されています。")
    pwd = st.text_input("合言葉を入力してください", type="password")
    
    if st.button("ログイン"):
        # Secretsからパスワードを取得
        target_pwd = os.getenv("APP_PASSWORD")
        if pwd == target_pwd:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("合言葉が違います。")
    return False

# --- メインコンテンツ（認証が通った時だけ表示） ---
if check_password():
    # サイドバーにログアウトと更新ボタン
    if st.sidebar.button("🔓 ログアウト"):
        st.session_state["password_correct"] = False
        st.rerun()
    
    if st.sidebar.button("🔄 データを最新にする"):
        st.cache_data.clear()
        st.rerun()

    st.title("📖 本のリサーチ・コレクション")

    # データ読み込み
    url = os.getenv("SPREADSHEET_URL")
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="5m")
    df = df.dropna(how="all")

    if not df.empty:
        # 1. 検索機能
        st.subheader("🔍 検索・絞り込み")
        search_query = st.text_input("キーワードを入力してね", "")

        if search_query:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        # 2. 統計表示
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="リサーチ総数", value=f"{len(df)} 件")
        
        # 3. 表の表示
        st.subheader("📋 リサーチリスト")
        try:
            display_df = df.sort_values(by=["巻", "ページ"]).reset_index(drop=True)
            
            # デザイン：交互に色をつけ、文字を中央寄りに
            st.dataframe(
                display_df.style.set_properties(**{
                    'background-color': '#f9f9f9',
                    'color': '#333333',
                    'border-color': '#e0e0e0'
                }).highlight_max(axis=0, subset=['巻'], color='#ffe4e1'),
                use_container_width=True
            )
        except Exception:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("スプレッドシートにデータがまだありません。")

    st.sidebar.markdown("---")
    st.sidebar.caption("管理者としてログイン中")

