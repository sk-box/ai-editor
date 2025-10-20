"""
記事評価ページ - AI編集者評価機能
生成された記事を8軸で評価し、改善提案を提示
"""
import os
import json
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from prompts import get_evaluator_prompt

# 環境変数読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="記事評価 - YAE",
    page_icon="⭐",
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


# セッション状態の初期化
if "survey_data" not in st.session_state:
    st.session_state.survey_data = ""

if "generated_article" not in st.session_state:
    st.session_state.generated_article = ""

if "article_data" not in st.session_state:
    st.session_state.article_data = {}

if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = {}


# ヘッダー
st.title("⭐ 記事評価")
st.caption("AI編集者が記事を8軸で評価し、改善提案を行います")

# ナビゲーション
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← 記事生成へ戻る"):
        st.switch_page("pages/1_📝_記事生成.py")
with col2:
    if st.button("🏠 ホームへ"):
        st.switch_page("app.py")
with col3:
    if st.session_state.evaluation_result:
        if st.button("次へ：記事改善 →"):
            st.switch_page("pages/3_✏️_記事改善.py")

st.markdown("---")

# 記事が未生成の場合 - 直接入力オプションを提供
if not st.session_state.generated_article:
    st.info("💡 記事生成ページから来るか、または既存の記事を直接貼り付けて評価できます")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("📝 記事生成ページへ →", use_container_width=True):
            st.switch_page("pages/1_📝_記事生成.py")

    with col_b:
        show_input = st.button("✏️ 記事を直接入力する", use_container_width=True)

    if show_input or "show_article_input" in st.session_state:
        st.session_state.show_article_input = True

        st.markdown("---")
        st.subheader("📝 記事とデータの入力")

        # アンケートデータ入力
        survey_input = st.text_area(
            "アンケートデータ（任意）",
            value=st.session_state.survey_data,
            height=150,
            placeholder="Q1: SNSで最もよく使うのは？\nA1: Instagram 68%...",
            help="記事のデータ整合性を確認する場合は、元のアンケートデータを入力してください"
        )

        # 記事タイトル入力
        article_title_input = st.text_input(
            "記事タイトル",
            value=st.session_state.article_data.get('title_candidates', [''])[0] if st.session_state.article_data else "",
            placeholder="例: 高校生の7割がInstagramを利用"
        )

        # 記事本文入力
        article_input = st.text_area(
            "記事本文（Markdown形式）",
            value=st.session_state.generated_article,
            height=400,
            placeholder="## はじめに\n\n高校生の約7割がInstagramを利用し...\n\n## 結果\n\n...",
            help="評価したい記事の本文を貼り付けてください"
        )

        if st.button("💾 保存して評価を開始", type="primary", use_container_width=True):
            if article_input:
                st.session_state.survey_data = survey_input
                st.session_state.generated_article = article_input
                st.session_state.article_data = {
                    "title_candidates": [article_title_input] if article_title_input else ["無題"],
                    "article_body": article_input
                }
                st.session_state.show_article_input = False
                st.success("✅ 記事を保存しました！下にスクロールして評価を実行してください。")
                st.rerun()
            else:
                st.warning("⚠️ 記事本文を入力してください")

    if not st.session_state.generated_article:
        st.stop()

# メインコンテンツを2カラムに分割
left_col, right_col = st.columns([1, 1])

# 左カラム：生成された記事の表示
with left_col:
    st.subheader("📰 評価対象の記事")

    article_data = st.session_state.article_data

    # タイトル
    if "title_candidates" in article_data and article_data["title_candidates"]:
        st.markdown(f"### {article_data['title_candidates'][0]}")

    # リード文
    if "lead" in article_data:
        st.info(article_data["lead"])

    # 記事本文
    if st.session_state.generated_article:
        with st.container():
            st.markdown(st.session_state.generated_article)

    # 記事の再編集
    st.markdown("---")
    if st.button("✏️ 記事を編集", use_container_width=True):
        st.session_state.show_article_input = True
        st.rerun()

# 右カラム：評価実行と結果表示
with right_col:
    st.subheader("🔍 品質評価")

    if st.button("🚀 記事を評価", type="primary", use_container_width=True):
        with st.spinner("AI編集者が評価中..."):
            try:
                # 評価用のコンテキスト作成
                context = f"""
【アンケートデータ】
{st.session_state.survey_data}

【生成された記事】
タイトル: {article_data.get('title_candidates', [''])[0]}
{st.session_state.generated_article}
"""

                # OpenAI APIを呼び出し
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": get_evaluator_prompt()},
                        {"role": "user", "content": f"以下の記事を評価してください。JSON形式で出力してください。\n\n{context}"}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )

                # レスポンスをパース
                result = response.choices[0].message.content
                evaluation_result = json.loads(result)

                # セッション状態に保存
                st.session_state.evaluation_result = evaluation_result

                st.success("✅ 評価が完了しました！")
                st.rerun()

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")

# 評価結果の表示
if st.session_state.evaluation_result:
    st.markdown("---")
    st.subheader("📊 評価結果")

    evaluation = st.session_state.evaluation_result

    # スコア表示
    if "scores" in evaluation:
        st.markdown("### 📈 8軸スコア")

        scores = evaluation["scores"]
        score_labels = {
            "naturalness_teen": "10代自然さ",
            "readability": "わかりやすさ",
            "structure": "記事構成",
            "bias_assertion": "偏り・断定",
            "ethics_safety": "倫理・配慮",
            "seo_basics": "SEO基礎",
            "brand_fit": "ブランド整合",
            "data_integrity": "データ整合性"
        }

        # スコアを2列で表示
        score_col1, score_col2 = st.columns(2)

        score_items = list(scores.items())
        half = len(score_items) // 2

        with score_col1:
            for key, value in score_items[:half]:
                label = score_labels.get(key, key)
                st.metric(label, f"{value}/5", delta=None)

        with score_col2:
            for key, value in score_items[half:]:
                label = score_labels.get(key, key)
                st.metric(label, f"{value}/5", delta=None)

        # 合計スコア
        if "total_score" in evaluation:
            st.markdown("---")
            st.metric("**総合スコア**", f"{evaluation['total_score']}/40")

    st.markdown("---")

    # 強みと弱み
    if "summary" in evaluation:
        st.markdown("### 💪 強みと改善点")

        summary = evaluation["summary"]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**✅ 強み**")
            if "strengths" in summary:
                for strength in summary["strengths"]:
                    st.success(f"• {strength}")

        with col2:
            st.markdown("**⚠️ 改善点**")
            if "weaknesses" in summary:
                for weakness in summary["weaknesses"]:
                    st.warning(f"• {weakness}")

    st.markdown("---")

    # 改善提案
    if "proposals" in evaluation and evaluation["proposals"]:
        st.markdown("### 💡 具体的な改善提案")

        for i, proposal in enumerate(evaluation["proposals"], 1):
            with st.expander(f"提案 {i}: {proposal.get('category', '改善案')}", expanded=True):
                if "before" in proposal and "after" in proposal:
                    st.markdown(f"**修正前:** {proposal['before']}")
                    st.markdown(f"**修正後:** {proposal['after']}")
                    if "reason" in proposal:
                        st.info(f"💡 理由: {proposal['reason']}")
                elif "issue" in proposal:
                    st.markdown(f"**問題点:** {proposal['issue']}")
                    if "suggestion" in proposal:
                        st.markdown(f"**提案:** {proposal['suggestion']}")

    # 次のステップ
    st.markdown("---")
    st.success("✅ 評価が完了しました！次は「記事改善」ページで対話しながら記事をブラッシュアップしましょう。")
    if st.button("次へ：記事改善ページ →", type="primary", use_container_width=True):
        st.switch_page("pages/3_✏️_記事改善.py")
