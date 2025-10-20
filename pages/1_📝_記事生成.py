"""
記事生成ページ - ライター機能
アンケートデータから記事草稿を生成
"""
import os
import json
from pathlib import Path
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from prompts import get_writer_prompt

# 環境変数読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="記事生成 - YAE",
    page_icon="📝",
    layout="wide"
)

# OpenAI クライアント初期化
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ OPENAI_API_KEYが設定されていません。.envファイルを確認してください。")
        st.stop()
    return OpenAI(api_key=api_key)

client = get_openai_client()


# サンプルデータ読み込み
def load_sample_data():
    """enqueteフォルダからサンプルデータを読み込み"""
    samples = {}
    enquete_dir = Path("enquete")

    if enquete_dir.exists():
        for file_path in enquete_dir.glob("*.md"):
            with open(file_path, "r", encoding="utf-8") as f:
                samples[file_path.stem] = f.read()

    return samples


# セッション状態の初期化
if "survey_data" not in st.session_state:
    st.session_state.survey_data = ""

if "generated_article" not in st.session_state:
    st.session_state.generated_article = ""

if "article_data" not in st.session_state:
    st.session_state.article_data = {}


# ヘッダー
st.title("📝 記事生成")
st.caption("アンケートデータから記事草稿を自動生成します")

# ナビゲーション
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("🏠 ホームへ戻る"):
        st.switch_page("app.py")
with col3:
    if st.session_state.generated_article:
        if st.button("次へ：記事評価 →"):
            st.switch_page("pages/2_⭐_記事評価.py")

st.markdown("---")

# メインコンテンツを2カラムに分割
left_col, right_col = st.columns([1, 1])

# 左カラム：アンケートデータ入力
with left_col:
    st.subheader("📊 アンケートデータ入力")

    # サンプルデータ選択
    samples = load_sample_data()

    if samples:
        st.markdown("**サンプルデータから選択**")
        sample_options = ["（選択してください）"] + list(samples.keys())
        selected_sample = st.selectbox(
            "サンプルを選択",
            sample_options,
            key="sample_selector"
        )

        if selected_sample != "（選択してください）":
            if st.button("📥 サンプルを読み込む", use_container_width=True):
                st.session_state.survey_data = samples[selected_sample]
                st.success(f"✅ {selected_sample} を読み込みました")
                st.rerun()

        st.markdown("---")

    # 手動入力
    st.markdown("**または手動入力**")
    survey_input = st.text_area(
        "アンケート結果を貼り付け",
        value=st.session_state.survey_data,
        height=400,
        placeholder="""例：
Q1: SNSで最もよく使うのは？
A1: Instagram 68%、X 21%、TikTok 9%

Q2: SNSを使う目的は？
A2: 「友達とのつながり」「情報収集」

自由回答：
・「友達の発信が一番リアル」
・「ニュースよりもコメント欄を見る」
"""
    )

    if st.button("💾 データを保存", use_container_width=True):
        st.session_state.survey_data = survey_input
        st.success("✅ データを保存しました")
        st.rerun()

    # 現在のデータ状態表示
    if st.session_state.survey_data:
        st.info(f"📌 現在のデータ: {len(st.session_state.survey_data)}文字")
    else:
        st.warning("⚠️ アンケートデータが未設定です")

# 右カラム：記事生成
with right_col:
    st.subheader("✨ 記事生成")

    if not st.session_state.survey_data:
        st.warning("⚠️ まず左側でアンケートデータを入力してください")
    else:
        st.markdown("**現在のアンケートデータ**")
        with st.expander("データを確認", expanded=False):
            st.text(st.session_state.survey_data[:500] + "..." if len(st.session_state.survey_data) > 500 else st.session_state.survey_data)

        st.markdown("---")

        if st.button("🚀 記事を生成", type="primary", use_container_width=True):
            with st.spinner("記事を生成中..."):
                try:
                    # OpenAI APIを呼び出し
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": get_writer_prompt()},
                            {"role": "user", "content": f"以下のアンケート結果から記事を作成してください。JSON形式で出力してください。\n\n{st.session_state.survey_data}"}
                        ],
                        temperature=0.7,
                        response_format={"type": "json_object"}
                    )

                    # レスポンスをパース
                    result = response.choices[0].message.content
                    article_data = json.loads(result)

                    # セッション状態に保存
                    st.session_state.article_data = article_data
                    st.session_state.generated_article = article_data.get("article_body", "")

                    st.success("✅ 記事生成が完了しました！")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ エラーが発生しました: {str(e)}")

# 生成結果の表示
if st.session_state.article_data:
    st.markdown("---")
    st.subheader("📄 生成結果")

    article_data = st.session_state.article_data

    # タイトル候補
    if "title_candidates" in article_data:
        st.markdown("**📌 タイトル候補**")
        for i, title in enumerate(article_data["title_candidates"], 1):
            st.markdown(f"{i}. {title}")
        st.markdown("---")

    # 要約
    if "summary" in article_data:
        st.markdown("**📝 要約**")
        st.info(article_data["summary"])
        st.markdown("---")

    # リード文
    if "lead" in article_data:
        st.markdown("**🎯 リード文**")
        st.write(article_data["lead"])
        st.markdown("---")

    # 記事本文
    if "article_body" in article_data:
        st.markdown("**📰 記事本文**")
        with st.container():
            st.markdown(article_data["article_body"])
        st.markdown("---")

    # 構成
    if "structure" in article_data:
        st.markdown("**📋 記事構成**")
        for i, section in enumerate(article_data["structure"], 1):
            st.markdown(f"{i}. {section}")

    # 次のステップ
    st.markdown("---")
    st.success("✅ 記事草稿が生成されました！次は「記事評価」ページで品質をチェックしましょう。")
    if st.button("次へ：記事評価ページ →", type="primary", use_container_width=True):
        st.switch_page("pages/2_⭐_記事評価.py")
