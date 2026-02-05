import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# 設定の読み込み
load_dotenv()

# ページの設定：ワイドモード
st.set_page_config(page_title="My Book Research", page_icon="📖", layout="wide")

# --- デザイン調整：全体の文字を少し小さくするCSS ---
st.markdown("""
    <style>
    html, body, [class*="st-"] {
        font-size: 13px;
    }
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
    # --- サイドバーの設定 ---
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

    # --- データの読み込み処理（ここを大幅に変更） ---
    @st.cache_data(ttl=300) # 5分間キャッシュ
    def load_data_from_gsheets(url):
        try:
            # URLをCSVエクスポート形式に変換
            csv_url = url.replace("/edit#gid=", "/export?format=csv&gid=")
            if "/export" not in csv_url:
                csv_url = url.split("/edit")[0] + "/export?format=csv"
            
            # pandasで読み込み
            data = pd.read_csv(csv_url)
            return data
        except Exception as e:
            st.error(f"データの読み込みに失敗しました: {e}")
            return pd.DataFrame()

    raw_url = os.getenv("SPREADSHEET_URL")
    df = load_data_from_gsheets(raw_url)
    df = df.dropna(how="all")

    if not df.empty:
        # 1. 検索機能
        st.subheader("🔍 検索・絞り込み")
        search_query = st.text_input("キーワードを入力してね（巻数や内容など）", "")

        if search_query:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        # 2. 統計表示
        st.metric(label="リサーチ総数", value=f"{len(df)} 件")
        
        # 3. 表の表示
        st.subheader("📋 リサーチリスト")
        try:
            # 列名が存在するか確認してからソート（エラー防止）
            sort_cols = [c for c in ["巻", "ページ"] if c in df.columns]
            if sort_cols:
                display_df = df.sort_values(by=sort_cols).reset_index(drop=True)
            else:
                display_df = df.reset_index(drop=True)
            
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
                        wrap=True 
                    ),
                },
                hide_index=True,
            )
        except Exception:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("データが読み込めないか、空っぽのようです。URLと共有設定を確認してね！")
        
