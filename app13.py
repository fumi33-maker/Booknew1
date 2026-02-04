import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from dotenv import load_dotenv

# 設定の読み込み
load_dotenv()

# ページの設定：ワイドモードで画面を広く使う
st.set_page_config(page_title="My Book Research", page_icon="📖", layout="wide")

# --- デザイン調整：全体の文字を少し小さくするCSS ---
st.markdown("""
    <style>
    html, body, [class*="st-"] {
        font-size: 13px; /* 全体のフォントサイズ */
    }
    div[data-testid="stDataFrame"] td {
        font-size: 12px; /* 表の中の文字をさらに少し小さく */
    }
    </style>
    """, unsafe_allow_html=True)

# --- パスワード認証機能 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # ログイン画面
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
    # --- サイドバーの設定（更新・ログアウト・コツ） ---
    with st.sidebar:
        if st.button("🔄 データを最新にする"):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("🔓 ログアウト"):
            st.session_state["password_correct"] = False
            st.rerun()
        
        st.markdown("---")
        st.write("💡 **コツ**")
        st.caption("スプレッドシートを更新したら、上の「更新ボタン」を押すと反映されるよ！")

    # タイトル
    st.title("📖 本のリサーチ・コレクション")

    # データ読み込み
    url = os.getenv("SPREADSHEET_URL")
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl="5m", encoding="utf-8")
    df = df.dropna(how="all")

    if not df.empty:
        # 1. 検索機能
        st.subheader("🔍 検索・絞り込み")
        search_query = st.text_input("キーワードを入力してね（巻数や内容など）", "")

        if search_query:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        # 2. 統計表示
        st.metric(label="リサーチ総数", value=f"{len(df)} 件")
        
        # 3. 表の表示（スマホ対応・折り返し設定）
        st.subheader("📋 リサーチリスト")
        try:
            # 巻とページで並び替え
            display_df = df.sort_values(by=["巻", "ページ"]).reset_index(drop=True)
            
            # 列の設定
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "巻": st.column_config.NumberColumn("巻", width=40),
                    "ページ": st.column_config.NumberColumn("頁", width=40),
                    "内容": st.column_config.TextColumn(
                        "内容", 
                        width=800, 
                        wrap=True  # ← ここがスマホで全文読むためのポイント！
                    ),
                },
                hide_index=True, # 左側の数字を消してスッキリ
            )
        except Exception:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("スプレッドシートにデータがまだありません。")

