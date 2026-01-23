import streamlit as st
from supabase import create_client
from datetime import datetime

# Supabase接続
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("📝 Supabaseメモ保存アプリ")

# メモ入力
memo = st.text_input("メモを入力してください")

if st.button("保存"):
    if memo.strip() != "":
        supabase.table("memos").insert({
            "content": memo,
            "created_at": datetime.now().isoformat()
        }).execute()
        st.success("メモを保存しました")
    else:
        st.warning("メモを入力してください")

st.divider()
st.subheader("📚 保存されたメモ一覧")

# メモ取得
response = supabase.table("memos") \
    .select("content, created_at") \
    .order("id", desc=True) \
    .execute()

for row in response.data:
    st.write(f"🕒 {row['created_at']}")
    st.write(row["content"])
    st.divider()
