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
            # URLの末尾をCSV形式へ修正
            target_url = url.replace("pubhtml", "pub?output=csv")
            if "output=csv" not in target_url:
                target_url = target_url + ("&" if "?" in target_url else "?") + "output=csv"
            
            # ブラウザのふりをしてアクセス
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(target_url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                # 【ここが重要！】エラー行をスキップし、柔軟な解析エンジンを使用する設定
                data = pd.read_csv(
                    response, 
                    on_bad_lines='skip',  # 壊れた行を読み飛ばす
                    engine='python',       # 柔軟な解析エンジン
                    sep=',',               # カンマ区切り
                    quotechar='"',         # 引用符の処理
                    encoding_errors='replace' # 文字化けを置換
                )
                
                # 列名の空白削除
                data.columns = [str(c).strip() for c in data.columns]
                return data
        except Exception as e:
            st.error(f"データの取得に失敗しました。Error: {e}")
            return pd.DataFrame()

    # .envからURLを取得
    csv_url = os.getenv("SPREADSHEET_URL")
    
    if csv_url:
        df = load_data(csv_url)
        
        # 不要な空行を削除
        if not df.empty:
            df = df.dropna(how="all")

        if not df.empty:
            st.subheader("🔍 検索・絞り込み")
            search_query = st.text_input("キーワード入力", "")
            if search_query:
                # 検索時にエラーが出ないよう文字列変換して処理
                df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]

            st.metric(label="リサーチ総数", value=f"{len(df)} 件")
            
            # 列の存在チェックをして設定を適用
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
            
            # 表示
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config=col_configs,
                hide_index=True
            )
        else:
            st.info("データが読み込めませんでした。URLの末尾が「pub?output=csv」になっているか、シートが「ウェブに公開」されているか確認してね。")
    else:
        st.warning("URLが設定されていません。")
