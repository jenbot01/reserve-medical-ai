import streamlit as st
import os
from openai import OpenAI

# --- CONFIGURATION ---
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ OpenAI API Key not found! Please add it to Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(page_title="The Reserve Medical", page_icon="🩺", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

    .stApp { background-color: #FAF7F2 !important; font-family: 'Inter', sans-serif !important; color: #2C2C2C !important; }

    /* Remove Avatars */
    .stChatMessageAvatar { display: none !important; }

    /* Message Alignment */
    div[data-testid="stChatMessage"] {
        padding: 1rem 0;
        background-color: transparent !important;
    }

    /* User (Right) */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        flex-direction: row-reverse;
        text-align: right;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) > div:first-child {
        margin-left: auto;
        margin-right: 0;
        background-color: #E8E0D4;
        padding: 10px 18px;
        border-radius: 18px 18px 0 18px;
        max-width: 80%;
        text-align: left;
    }

    /* AI (Left) */
    div[data-testid="stChatMessage"]:nth-child(even) > div:first-child {
        margin-right: auto;
        margin-left: 0;
        background-color: transparent;
        padding: 0;
        max-width: 90%;
        text-align: left;
    }

    /* Hide Branding */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are The Reserve Medical Assistant.
TONE: Professional, warm, authoritative.
FORMAT: No numbers. Bold the **Condition Name** only.

STRUCTURE:

**Clinical Impression**
(Discuss most likely cause.)

**Differential Diagnosis**
(Discuss less likely causes.)

**Emergent Warnings**
(Only if applicable.)

**AI Recommendation**
(Triage level: Home Care, Appointment, Urgent Care, ER. Text only.)

**References**
(Link to trusted sources.)
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CHAT DISPLAY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- INPUT AREA ---
if prompt := st.chat_input("Message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        messages_api = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]
        
        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_api,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error: {e}")
