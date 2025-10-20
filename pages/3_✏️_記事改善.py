"""
記事改善ページ - 編集者チャット機能
対話形式で記事をブラッシュアップ
"""
import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from prompts import get_system_prompt

# 環境変数読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="記事改善 - YAE",
    page_icon="✏️",
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

if "improvement_messages" not in st.session_state:
    st.session_state.improvement_messages = []

if "current_article" not in st.session_state:
    st.session_state.current_article = st.session_state.generated_article


# ヘッダー
st.title("✏️ 記事改善")
st.caption("AI編集者と対話しながら記事をブラッシュアップします")

# ナビゲーション
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← 記事評価へ戻る"):
        st.switch_page("pages/2_⭐_記事評価.py")
with col2:
    if st.button("🏠 ホームへ"):
        st.switch_page("app.py")

st.markdown("---")

# 記事が未生成の場合 - 直接入力オプションを提供
if not st.session_state.generated_article:
    st.info("💡 記事生成・評価ページから来るか、または既存の記事を直接貼り付けて改善できます")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("📝 記事生成へ →", use_container_width=True):
            st.switch_page("pages/1_📝_記事生成.py")

    with col_b:
        if st.button("⭐ 記事評価へ →", use_container_width=True):
            st.switch_page("pages/2_⭐_記事評価.py")

    with col_c:
        show_input = st.button("✏️ 記事を直接入力", use_container_width=True)

    if show_input or "show_improvement_input" in st.session_state:
        st.session_state.show_improvement_input = True

        st.markdown("---")
        st.subheader("📝 記事の入力")

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
            help="改善したい記事の本文を貼り付けてください"
        )

        if st.button("💾 保存して改善を開始", type="primary", use_container_width=True):
            if article_input:
                st.session_state.generated_article = article_input
                st.session_state.current_article = article_input
                st.session_state.article_data = {
                    "title_candidates": [article_title_input] if article_title_input else ["無題"],
                    "article_body": article_input
                }
                st.session_state.show_improvement_input = False
                st.success("✅ 記事を保存しました！チャットで改善を始めましょう。")
                st.rerun()
            else:
                st.warning("⚠️ 記事本文を入力してください")

    if not st.session_state.generated_article:
        st.stop()

# サイドバー：現在の記事と評価結果
with st.sidebar:
    st.title("📄 現在の記事")

    # タイトル表示
    if st.session_state.article_data and "title_candidates" in st.session_state.article_data:
        st.markdown(f"### {st.session_state.article_data['title_candidates'][0]}")

    st.markdown("---")

    # 記事本文のプレビュー
    st.subheader("記事本文")
    with st.expander("全文を表示", expanded=False):
        st.markdown(st.session_state.current_article)

    st.markdown("---")

    # 評価結果のサマリー
    if st.session_state.evaluation_result:
        st.subheader("⭐ 評価サマリー")

        if "total_score" in st.session_state.evaluation_result:
            st.metric("総合スコア", f"{st.session_state.evaluation_result['total_score']}/40")

        if "summary" in st.session_state.evaluation_result:
            summary = st.session_state.evaluation_result["summary"]

            if "weaknesses" in summary and summary["weaknesses"]:
                st.markdown("**主な改善点:**")
                for weakness in summary["weaknesses"][:3]:
                    st.warning(f"• {weakness}")

    st.markdown("---")

    # チャットリセット
    if st.button("🔄 チャットをリセット", use_container_width=True):
        st.session_state.improvement_messages = []
        st.session_state.current_article = st.session_state.generated_article
        st.rerun()

    # 記事を編集
    if st.button("✏️ 記事を編集", use_container_width=True):
        st.session_state.show_improvement_input = True
        st.rerun()

    # 記事をダウンロード
    st.markdown("---")
    st.subheader("💾 記事を保存")

    download_content = f"""# {st.session_state.article_data.get('title_candidates', ['記事タイトル'])[0]}

{st.session_state.current_article}

---
生成日: {st.session_state.get('generation_date', 'N/A')}
YAE (Young AI Editor) で生成
"""

    st.download_button(
        label="📥 Markdown形式でダウンロード",
        data=download_content,
        file_name="article.md",
        mime="text/markdown",
        use_container_width=True
    )


# メインエリア：チャット画面
st.subheader("💬 AI編集者とチャット")

# 初回メッセージ
if len(st.session_state.improvement_messages) == 0:
    with st.chat_message("assistant"):
        initial_message = """
こんにちは！AI編集者です✍️

記事の評価が完了しました。これから対話を通じて記事を改善していきましょう。

**できること:**
- 文体の調整（「もっとカジュアルに」「丁寧に」など）
- 見出しの変更・追加
- 自由回答の追加・削除
- 構成の変更
- 特定の表現の修正

**使い方の例:**
- 「タイトルをもっとキャッチーにして」
- 「自由回答をもう2つ追加して」
- 「第2段落をもっと簡潔にして」
- 「見出しを3つに分けて」

何から始めましょうか？
"""
        st.markdown(initial_message)

# チャット履歴の表示
for message in st.session_state.improvement_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力
if prompt := st.chat_input("改善の指示を入力（例: タイトルをもっとキャッチーにして）"):

    # ユーザーメッセージを追加
    st.session_state.improvement_messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # AI編集者のレスポンス生成
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # コンテキスト作成
        context_message = f"""
【参考情報】

アンケートデータ:
{st.session_state.survey_data}

現在の記事:
{st.session_state.current_article}

評価結果:
{st.session_state.evaluation_result.get('summary', {})}
"""

        # OpenAI APIを呼び出し
        try:
            # メッセージ構築
            messages = [
                {"role": "system", "content": get_system_prompt()}
            ]

            # 最初のメッセージにコンテキストを追加
            if len(st.session_state.improvement_messages) == 1:
                messages.append({
                    "role": "user",
                    "content": context_message + "\n\n" + prompt
                })
            else:
                # チャット履歴を追加
                for msg in st.session_state.improvement_messages:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            # レスポンス取得
            message_placeholder.markdown("💭 考え中...")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                stream=False
            )

            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)

            # アシスタントメッセージを履歴に追加
            st.session_state.improvement_messages.append({
                "role": "assistant",
                "content": full_response
            })

            # 記事が更新された場合は current_article を更新
            # (実際には、AIの回答から記事部分を抽出する必要がありますが、
            #  ここでは簡易的に全レスポンスを記録)

        except Exception as e:
            st.error(f"❌ エラーが発生しました: {str(e)}")


# フッター情報
st.markdown("---")
st.info("""
💡 **ヒント:**
- 具体的な指示を出すほど、的確な修正が得られます
- 「見出しを変えて」ではなく「見出しをもっとわかりやすく、10代に刺さる表現にして」
- 修正後の記事は左サイドバーからダウンロードできます
""")
