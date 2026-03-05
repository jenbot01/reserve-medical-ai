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

    /* Centered Hero Header */
    .hero-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        height: 60vh; text-align: center;
    }
    
    h1 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #1A1A1A !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-size: 3rem !important;
        margin-bottom: 10px;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif; color: #666; font-size: 0.9rem;
        text-transform: uppercase; letter-spacing: 2px; margin-bottom: 40px;
    }

    /* Links */
    a { color: #C5A059 !important; text-decoration: none !important; font-weight: 600 !important; }
    
    /* Input Box (Default Bottom) */
    .stChatInput { bottom: 40px !important; }

    /* Hide Branding */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are The Reserve Medical Assistant. You provide clinical intelligence, not advice.
TONE: Professional, warm, human, authoritative.
FORMAT: No numbers. Bold key diagnoses.

STRUCTURE:

**Clinical Impression**
(Discuss most likely cause. Bold the condition name.)

**Differential Diagnosis**
(Discuss less likely causes. Bold condition names.)

**Emergent Warnings**
(Only if applicable. Serious tone.)

**AI Recommendation**
(Triage level: Home Care, Appointment, Urgent Care, ER. No colored dots. Just text.)

**References**
(Link to trusted sources like CDC/NIH/Mayo.)
"""

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- HERO VS CHAT MODE ---
if not st.session_state.messages:
    # HERO MODE (Centered)
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown("<h1>THE RESERVE MEDICAL</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>AI-Powered Clinical Intelligence</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # CHAT MODE (Top Header)
    st.markdown("<h1 style='font-size: 1.5rem !important; margin-top: 20px;'>THE RESERVE MEDICAL</h1>", unsafe_allow_html=True)
    
    # Display History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- INPUT AREA ---
prompt_placeholder = "Describe your symptoms..." if not st.session_state.messages else "Message..."

if prompt := st.chat_input(prompt_placeholder):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Force Rerun to switch from Hero to Chat layout immediately
    st.rerun()

# --- AI RESPONSE LOGIC (After Rerun) ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
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
