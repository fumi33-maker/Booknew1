import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from dotenv import load_dotenv

# 設定の読み込み
load_dotenv()

# ページの設定（少し広く、可愛く）
st.set_page_config(page_title="My Book Research", page_icon="📖", layout="wide")

# --- パスワード認証機能（ここを追加） ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # ログイン画面の表示
    st.title("🔒 認証が必要です")
    pwd = st.text_input("合言葉を入力してください", type="password")
    
    if st.button("ログイン"):
        target_pwd = os.getenv("APP_PASSWORD")
        if pwd == target_pwd:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("合言葉が違います。")
    return False

# --- メインコンテンツ（認証が通った時だけ表示） ---
if check_password():
    # タイトル
    st.title("📖 本のリサーチ・コレクション")

    # --- データ読み込み ---
    url = os.getenv("SPREADSHEET_URL")
    conn = st.connection("gsheets", type=GSheetsConnection)

    # データを読み込んで、空行を削除
    # エラー対策で encoding="utf-8" を念のため追加
    df = conn.read(spreadsheet=url, ttl="5m", encoding="utf-8")
    df = df.dropna(how="all")

    if not df.empty:
        # --- 1. 検索機能エリア ---
        st.subheader("🔍 検索・絞り込み")
        search_query = st.text_input("キーワードを入力してね（巻数や内容など）", "")

        # 検索機能のロジック
        if search_query:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        # --- 2. 統計表示 ---
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="リサーチ総数", value=f"{len(df)} 件")
        
        # --- 3. 表の表示 ---
        st.subheader("📋 リサーチリスト")
        
        try:
            display_df = df.sort_values(by=["巻", "ページ"]).reset_index(drop=True)
            
            st.dataframe(
                display_df.style.set_properties(**{
                    'background-color': '#f0f2f6',
                    'color': '#31333F',
                    'border-color': 'white'
                }).highlight_max(axis=0, subset=['巻'], color='#ffebf0'),
                use_container_width=True
            )
        except Exception:
            st.dataframe(df, use_container_width=True)

        # --- 4. 更新ボタン ---
        if st.sidebar.button("🔄 データを最新にする"):
            st.cache_data.clear()
            st.rerun()
        
        # ログアウトボタンも追加
        if st.sidebar.button("🔓 ログアウト"):
            st.session_state["password_correct"] = False
            st.rerun()

    else:
        st.info("スプレッドシートにデータがまだありません。入力して待っててね！")

    # サイドバーのメッセージ
    st.sidebar.markdown("---")
    st.sidebar.write("💡 **コツ**")
    st.sidebar.caption("スプレッドシートを更新したら、上のボタンを押すとすぐに反映されるよ！")


