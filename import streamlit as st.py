import streamlit as st
from supabase import create_client

# 1. Supabase接続設定
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🚀 スコア保存機能付き！5問クイズ")

# セッション状態の初期化
if "question_idx" not in st.session_state:
    st.session_state.question_idx = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "data_saved" not in st.session_state:
    st.session_state.data_saved = False
if "answered" not in st.session_state:
    st.session_state.answered = False

# 2. データベースから問題を取得（最大5問に制限）
#@st.cache_data
def fetch_questions():
    # .limit(5) を追加して最大5問にしています
    response = supabase.table("quiz_questions").select("*").limit(5).execute()
    return response.data

questions = fetch_questions()

# クイズの進行管理
if st.session_state.question_idx < len(questions):
    q = questions[st.session_state.question_idx]
    
    st.subheader(f"問題 {st.session_state.question_idx + 1} / {len(questions)}")
    st.write(f"**{q['question']}**")
    
    # ラジオボタンの選択肢（一意のキーを持たせる）
    choice = st.radio("答えを選んでください:", q["options"], key=f"q_{st.session_state.question_idx}")
    
    # 回答ボタン
    if not st.session_state.answered:
        if st.button("回答する"):
            st.session_state.answered = True
            st.rerun()

    # 回答した後の処理
    if st.session_state.answered:
        correct_answer = q["options"][q["answer_index"]]
        if choice == correct_answer:
            st.success("正解！✨")
            # スコア加算処理（まだ加算していなければ）
            if "last_scored_idx" not in st.session_state or st.session_state.last_scored_idx < st.session_state.question_idx:
                st.session_state.score += 1
                st.session_state.last_scored_idx = st.session_state.question_idx
        else:
            st.error(f"不正解... 答えは「{correct_answer}」でした。")
        
        st.info(f"解説: {q['explanation']}")
        
        # 次へボタン
        if st.button("次の問題へ"):
            st.session_state.question_idx += 1
            st.session_state.answered = False # 回答状態をリセット
            st.rerun()

else:
    # 3. 結果表示 & データの保存
    st.balloons()
    st.header("🎉 全問題終了！")
    final_score = st.session_state.score
    total_q = len(questions)
    st.markdown(f"### あなたの最終スコア: `{final_score}` / `{total_q}`")
    
    # スコアを一度だけ保存
    if not st.session_state.data_saved:
        log_data = {
            "score": final_score,
            "total_questions": total_q
        }
        supabase.table("quiz_logs").insert(log_data).execute()
        st.session_state.data_saved = True
        st.success("今回の利用データをSupabaseに永続保存しました。")

    st.divider()
    st.subheader("📚 過去の履歴（最新5件）")
    
    # 履歴を表示
    logs = supabase.table("quiz_logs").select("*").order("created_at", desc=True).limit(5).execute()
    if logs.data:
        for entry in logs.data:
            st.write(f"📅 {entry['created_at'][:10]} | スコア: {entry['score']} / {entry['total_questions']}")
    
    if st.button("もう一度最初から挑戦する"):
        # 全状態をクリア
        st.session_state.question_idx = 0
        st.session_state.score = 0
        st.session_state.data_saved = False
        st.session_state.answered = False
        if "last_scored_idx" in st.session_state:
            del st.session_state.last_scored_idx
        st.rerun()

