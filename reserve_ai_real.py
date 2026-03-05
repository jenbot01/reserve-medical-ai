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

    /* Global Reset */
    .stApp { background-color: #FAF7F2 !important; font-family: 'Inter', sans-serif !important; color: #2C2C2C !important; }
    
    /* Hide Cruft */
    .stChatMessageAvatar { display: none !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* HOME PAGE HERO */
    .hero-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        height: 70vh; /* Vertically Center */
        text-align: center;
    }
    
    /* Header Font (Big Serif) */
    .hero-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3.5rem;
        color: #1A1A1A;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 40px;
    }

    /* Input Box (Borderless) */
    .stTextInput input {
        border: none !important;
        border-bottom: 1px solid #ddd !important; /* Subtle underline */
        background-color: transparent !important;
        text-align: center;
        font-size: 1.1rem;
        padding: 10px;
    }
    .stTextInput input:focus {
        border-bottom: 1px solid #C5A059 !important; /* Gold accent on focus */
        box-shadow: none !important;
    }

    /* Button Styling */
    .stButton button {
        background-color: #1A1A1A !important;
        color: white !important;
        border-radius: 30px !important;
        padding: 10px 30px !important;
        font-family: 'Inter', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.8rem !important;
        border: none !important;
        margin-top: 20px !important;
    }
    
    /* CHAT ALIGNMENT */
    div[data-testid="stChatMessage"]:nth-child(odd) { flex-direction: row-reverse; text-align: right; }
    div[data-testid="stChatMessage"]:nth-child(odd) > div:first-child {
        background-color: #E8E0D4; padding: 12px 20px; border-radius: 20px 20px 0 20px; text-align: left;
    }
    div[data-testid="stChatMessage"]:nth-child(even) { text-align: left; }
    div[data-testid="stChatMessage"]:nth-child(even) > div:first-child {
        background-color: transparent; padding: 0;
    }

</style>
""", unsafe_allow_html=True)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are The Reserve Medical Assistant.
TONE: Professional, warm, authoritative.
FORMAT: Bold the **Condition Name** only. No numbers.

STRUCTURE:
**Clinical Impression**
(Most likely cause.)

**Differential Diagnosis**
(Less likely causes.)

**Emergent Warnings**
(If applicable.)

**AI Recommendation**
(Triage level.)

**References**
(Links.)
"""

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- PAGE LOGIC ---
if not st.session_state.messages:
    # --- HERO MODE ---
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">THE RESERVE MEDICAL</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">AI-Powered Clinical Intelligence</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Simple Centered Form (Input + Button)
    col1, col2, col3 = st.columns([1, 2, 1]) # Center column
    with col2:
        with st.form("hero_form"):
            user_input = st.text_input("Describe your symptoms...", placeholder="Describe your symptoms...", label_visibility="collapsed")
            submitted = st.form_submit_button("Start Consultation", use_container_width=True)
            
            if submitted and user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.rerun()

else:
    # --- CHAT MODE ---
    st.markdown("<h1 style='font-family: Cormorant Garamond; font-size: 1.8rem; text-align: center; margin-top: 20px; text-transform: uppercase;'>THE RESERVE MEDICAL</h1>", unsafe_allow_html=True)
    
    # History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Input
    if prompt := st.chat_input("Continue consultation..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # Response
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
