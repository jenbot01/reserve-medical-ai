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

# --- CUSTOM CSS (Warm Claude Style) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

    .stApp { background-color: #FAF7F2 !important; font-family: 'Inter', sans-serif !important; color: #2C2C2C !important; }

    h1 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #1A1A1A !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-size: 2.5rem !important;
        text-align: center;
        margin-bottom: 0px;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #666;
        text-align: center;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: -10px;
        margin-bottom: 40px;
    }

    /* Links */
    a { color: #C5A059 !important; text-decoration: none !important; font-weight: 500 !important; }
    a:hover { text-decoration: underline !important; }

    /* Messages */
    .stChatMessage { background-color: transparent !important; border: none !important; }
    div[data-testid="stChatMessage"]:nth-child(odd) { flex-direction: row-reverse; text-align: right; }
    div[data-testid="stChatMessage"]:nth-child(odd) .stMarkdown {
        background-color: #E8E0D4; padding: 12px 20px; border-radius: 20px;
        display: inline-block; max-width: 80%; text-align: left;
    }
    div[data-testid="stChatMessage"]:nth-child(even) .stMarkdown {
        background-color: transparent; padding: 10px 0; color: #2C2C2C;
        font-family: 'Inter', sans-serif; line-height: 1.6; font-size: 1.05rem;
    }

    /* Input Box */
    .stChatInput { position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); width: 100%; max-width: 700px; z-index: 999; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1>THE RESERVE MEDICAL</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>AI-Powered Clinical Intelligence</p>", unsafe_allow_html=True)

# --- SYSTEM PROMPT (With Citations) ---
SYSTEM_PROMPT = """
You are The Reserve Medical Assistant. You provide clinical intelligence, not advice.
TONE: Professional, warm, human, and authoritative.

STRUCTURE:

1. **Clinical Impression (Most Likely):**
   - Discuss the most probable cause. Explain *why*.

2. **Differential Diagnosis (Less Likely):**
   - Discuss other possibilities ("Less likely, but worth considering...").

3. **Critical Rule-Outs (Emergent Warnings):**
   - Mention serious conditions IF applicable.

4. **Clinical References:**
   - Provide direct links to trusted sources (CDC, NIH, Mayo Clinic, Cleveland Clinic) for further reading.
   - Format: "[Source Name](URL)"

5. **AI Recommendation:**
   - 🟢 Home Care / 🟡 Appointment / 🔴 ER.
   - **Explicit Warning:** "Go immediately to the Emergency Room if..."

SAFETY: If emergent (chest pain/stroke/airway), start with "🔴 GO TO ER IMMEDIATELY" and skip the differential.
"""

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CHAT DISPLAY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- INPUT AREA ---
if prompt := st.chat_input("Consult The Reserve..."):
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
