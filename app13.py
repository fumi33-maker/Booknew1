import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# ページの設定
st.set_page_config(page_title="My Book Research", page_icon="📖", layout="wide")

# --- 文字サイズと表の微調整用CSS ---
st.markdown("""
    <style>
    html, body, [class*="st-"] {
        font-size: 13px; /* 全体をさらに少し小さく */
    }
    /* 表の中の文字サイズを調整 */
    div[data-testid="stDataFrame"] td {
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- パスワード認証機能 ---
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
    # --- サイドバーの設定（復活！） ---
    with st.sidebar:
        if st.button("🔓 ログアウト"):
            st.session_state["password_correct"] = False
            st.rerun()
        
        if st.button("🔄 データを最新にする"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.write("💡 **コツ**")
        st.caption("スプレッドシートを更新したら、上のボタンを押すとすぐに反映されるよ！")

    # --- メイン画面 ---
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
        
        # 3. 表の表示（列幅を限界まで調整）
        st.subheader("📋 リサーチリスト")
        
        try:
            display_df = df.sort_values(by=["巻", "ページ"]).reset_index(drop=True)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "巻": st.column_config.NumberColumn("巻", width=40),      # 幅をピクセルで最小指定
                    "ページ": st.column_config.NumberColumn("頁", width=40),  # 「ページ」から「頁」へ短縮
                    "内容": st.column_config.TextColumn("内容", width=800),    # ここを最大級に広く
                },
                hide_index=True,
            )
        except Exception:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("スプレッドシートにデータがまだありません。")
        
