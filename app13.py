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

    # キャッシュをクリアしやすく設定
    @st.cache_data(ttl=10)
    def load_data(url):
        try:
            # 直接pandasで読み込む（これが一番エラーが出にくい）
            df = pd.read_csv(url)
            # 列名の前後に空白があれば削除
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"取得エラー: {e}")
            return pd.DataFrame()

    # SecretsからURLを取得
    csv_url = os.getenv("SPREADSHEET_URL")
    
    if csv_url:
        df = load_data(csv_url)
        
        if not df.empty:
            # Googleのログイン画面を誤って読んだ場合の対策
            if "Copyright" in str(df.columns) or "html" in str(df.columns).lower():
                st.error("まだGoogleが古いデータを返しています。数分待つか、Rebootしてください。")
            else:
                st.subheader("🔍 検索")
                search_query = st.text_input("キーワード入力", "")
                
                # 検索処理
                if search_query:
                    df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]

                st.metric(label="リサーチ総数", value=f"{len(df)} 件")
                
                # 列の設定（巻、ページ、内容に対応）
                col_configs = {
                    "巻": st.column_config.NumberColumn("巻", width=60),
                    "ページ": st.column_config.NumberColumn("ページ", width=60),
                    "内容": st.column_config.TextColumn("内容", width=800, wrap=True)
                }

                # 表示
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config=col_configs,
                    hide_index=True
                )
        else:
            st.info("データが空か、読み込み中です。")
    else:
        st.warning("URLが設定されていません。")
