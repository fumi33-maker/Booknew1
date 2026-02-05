import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="My Book Research", page_icon="📖", layout="wide")

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
    st.title("📖 本のリサーチ・コレクション")

    @st.cache_data(ttl=60)
    def load_data(url):
        try:
            # 余計な加工をせず、直接pandasで読み込む
            return pd.read_csv(url)
        except Exception as e:
            st.error(f"取得エラー: {e}")
            return pd.DataFrame()

    # URLは必ず export?format=csv のものを使用
    csv_url = os.getenv("SPREADSHEET_URL")
    
    if csv_url:
        df = load_data(csv_url)
        if not df.empty and "Copyright" not in str(df.columns):
            st.metric(label="リサーチ総数", value=f"{len(df)} 件")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.error("Googleがデータを拒否しました。URLをブラウザで開いてファイルが落ちてくるか確認してください。")
            st.info(f"現在のURL設定: {csv_url}")
