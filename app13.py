import streamlit as st
import pandas as pd
import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="My Book Research", page_icon="📖", layout="wide")

# --- デザインCSS ---
st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 13px; }
    div[data-testid="stDataFrame"] td { font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- パスワード認証 ---
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
    with st.sidebar:
        if st.button("🔄 データを最新にする"):
            st.cache_data.clear()
            st.rerun()
        if st.button("🔓 ログアウト"):
            st.session_state["password_correct"] = False
            st.rerun()

    st.title("📖 本のリサーチ・コレクション")

    @st.cache_data(ttl=300)
    def load_data(url):
        try:
            # URLの末尾を強制的にCSV形式へ修正
            target_url = url.replace("pubhtml", "pub?output=csv")
            if "output=csv" not in target_url:
                target_url = target_url + ("&" if "?" in target_url else "?") + "output=csv"
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(target_url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                data = pd.read_csv(response)
                # 【重要】列名の前後の空白を削除して、一致しやすくする
                data.columns = [str(c).strip() for c in data.columns]
                return data
        except Exception as e:
            st.error(f"データの取得に失敗しました。Error: {e}")
            return pd.DataFrame()

    csv_url = os.getenv("SPREADSHEET_URL")
    
    if csv_url:
        df = load_data(csv_url)
        df = df.dropna(how="all")

        if not df.empty:
            st.subheader("🔍 検索・絞り込み")
            search_query = st.text_input("キーワード入力", "")
            if search_query:
                df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]

            st.metric(label="リサーチ総数", value=f"{len(df)} 件")
            
            # 列の存在チェックをしてから表示
            col_configs = {}
            if "内容" in df.columns:
                col_configs["内容"] = st.column_config.TextColumn("内容", width=800, wrap=True)
            if "巻" in df.columns:
                col_configs["巻"] = st.column_config.NumberColumn("巻", width=40)
            if "ページ" in df.columns:
                col_configs["ページ"] = st.column_config.NumberColumn("頁", width=40)

            # 並び替え（存在する列のみ）
            sort_cols = [c for c in ["巻", "ページ"] if c in df.columns]
            display_df = df.sort_values(by=sort_cols).reset_index(drop=True) if sort_cols else df
            
            # エラー回避のため、configを安全に適用
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config=col_configs,
                hide_index=True
            )
        else:
            st.info("データが空か、読み込めませんでした。")
            
