"""
YAE (Young AI Editor) - ホームページ
"""
import os
import streamlit as st
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="YAE - AI編集者",
    page_icon="✍️",
    layout="wide"
)

# セッション状態の初期化
if "survey_data" not in st.session_state:
    st.session_state.survey_data = ""

if "generated_article" not in st.session_state:
    st.session_state.generated_article = ""

if "article_title" not in st.session_state:
    st.session_state.article_title = ""

if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = {}


# ヘッダー
st.title("✍️ YAE - AI編集者")
st.caption("10代向けメディア「ワカモノリサーチ」のAI編集アシスタント")

st.markdown("---")

# 概要説明
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📝 1. 記事生成")
    st.markdown("""
    **ライター機能**

    - アンケートデータ入力
    - AI記事草稿の自動生成
    - タイトル案・構成案の提示
    - 要約文の生成
    """)
    if st.button("記事生成ページへ →", use_container_width=True):
        st.switch_page("pages/1_📝_記事生成.py")

with col2:
    st.markdown("### ⭐ 2. 記事評価")
    st.markdown("""
    **編集者評価機能**

    - 8軸品質評価
    - スコア表示とコメント
    - 具体的な改善提案
    - データ整合性チェック
    """)
    if st.button("記事評価ページへ →", use_container_width=True):
        st.switch_page("pages/2_⭐_記事評価.py")

with col3:
    st.markdown("### ✏️ 3. 記事改善")
    st.markdown("""
    **編集者チャット機能**

    - 対話形式での記事修正
    - 改善案の段階的適用
    - 最終下書きの出力
    - WordPress連携準備
    """)
    if st.button("記事改善ページへ →", use_container_width=True):
        st.switch_page("pages/3_✏️_記事改善.py")

st.markdown("---")

# ワークフロー図
st.markdown("### 📊 使い方の流れ")
st.markdown("""
```
1. 📝 記事生成
   ↓ アンケートデータを入力して記事草稿を生成

2. ⭐ 記事評価
   ↓ AI編集者が8軸で品質評価・改善提案

3. ✏️ 記事改善
   ↓ チャット形式で対話しながら記事をブラッシュアップ

4. ✅ 完成
   → WordPress下書きとして出力
```
""")

# 現在のステータス表示
st.markdown("---")
st.markdown("### 📌 現在のステータス")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    if st.session_state.survey_data:
        st.success(f"✅ アンケートデータ: {len(st.session_state.survey_data)}文字")
    else:
        st.warning("⚠️ アンケートデータ未設定")

with status_col2:
    if st.session_state.generated_article:
        st.success(f"✅ 記事草稿生成済み")
    else:
        st.info("📝 記事未生成")

with status_col3:
    if st.session_state.evaluation_result:
        st.success(f"✅ 評価完了")
    else:
        st.info("⭐ 評価未実施")

# フッター
st.markdown("---")
st.markdown("""
**YAE（Young AI Editor）について**

ワカモノリサーチの記事制作を支援するAI編集ツールです。
アンケートデータから記事を生成し、品質評価・改善提案を通じて、
10代読者に届く自然で信頼できる記事作成をサポートします。

- 対象読者：10代（主に高校生）
- 文体：自然で読みやすい「です・ます調」
- 評価軸：8軸（自然さ、わかりやすさ、構成、偏り、倫理、SEO、ブランド、データ整合性）
""")

# API設定確認
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ OPENAI_API_KEYが設定されていません。.envファイルを確認してください。")
