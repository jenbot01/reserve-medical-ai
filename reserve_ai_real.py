import streamlit as st
import os
from openai import OpenAI

# --- CONFIGURATION ---
# Get the key from the environment (Streamlit Secrets)
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ OpenAI API Key not found! Please add it to Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(page_title="Reserve Medical AI", page_icon="🩺", layout="centered")

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are The Reserve Medical Assistant. You provide medical information, not advice.

STRUCTURE YOUR ANSWERS LIKE THIS:
1. **Common Possibilities:** List 1-2 likely causes based on symptoms.
2. **⚠️ Must Rule Out (Important):** List 1-2 serious conditions if applicable.
3. **AI Recommendation:**
   - Give a triage level: 🟢 Home Care, 🟡 Schedule Appointment (1-3 Days), 🟠 Urgent Care, or 🔴 ER.
   - List 2-3 specific "Red Flag" symptoms to watch for.

TONE: Professional, empathetic, concise.
SAFETY: If the user mentions chest pain, severe bleeding, or difficulty breathing, START with "🔴 GO TO ER IMMEDIATELY".
"""

# --- UI STYLING (Mobile-ish) ---
st.markdown("""
<style>
    .chat-container {
        max-width: 400px; margin: auto; border: 1px solid #ddd; border-radius: 20px; 
        padding: 20px; background-color: #f9f9f9; height: 500px; overflow-y: scroll;
        display: flex; flex-direction: column;
    }
    .user-msg {
        background-color: #007AFF; color: white; padding: 10px 15px; border-radius: 15px 15px 0 15px; 
        margin: 5px 0; align-self: flex-end; max-width: 80%;
    }
    .ai-msg {
        background-color: #E5E5EA; color: black; padding: 10px 15px; border-radius: 15px 15px 15px 0; 
        margin: 5px 0; align-self: flex-start; max-width: 80%;
    }
    .disclaimer { font-size: 0.7em; color: #888; text-align: center; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🩺 Reserve Medical AI")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        role_class = "user-msg" if msg["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("Type your symptoms...", key="input")
    submit_button = st.form_submit_button(label='Send')

if submit_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        ai_reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown('<p class="disclaimer">⚠️ Not medical advice. Educational only.</p>', unsafe_allow_html=True)
