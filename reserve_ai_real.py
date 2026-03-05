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

# --- CUSTOM CSS (Minimal & Stable) ---
st.markdown("""
<style>
    /* Font Imports */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

    /* Global Reset */
    .stApp { background-color: #FAF7F2; font-family: 'Inter', sans-serif; color: #2C2C2C; }
    
    /* Header Styling */
    h1 { font-family: 'Cormorant Garamond', serif; color: #1A1A1A; text-align: center; font-weight: 700; }
    
    /* Hide Avatars & Streamlit Branding */
    .stChatMessageAvatar { display: none !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* MESSAGE ALIGNMENT (The Critical Part) */
    div[data-testid="stChatMessage"] {
        padding: 1rem 0;
        background-color: transparent;
        border: none;
    }

    /* USER: Right Aligned Bubble */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        flex-direction: row-reverse;
        text-align: right;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) > div:first-child {
        background-color: #E8E0D4;
        color: #2C2C2C;
        padding: 10px 18px;
        border-radius: 18px 18px 0 18px;
        text-align: left;
        display: inline-block;
        max-width: 80%;
    }

    /* AI: Left Aligned Text */
    div[data-testid="stChatMessage"]:nth-child(even) {
        flex-direction: row;
        text-align: left;
    }
    div[data-testid="stChatMessage"]:nth-child(even) > div:first-child {
        background-color: transparent;
        padding: 0;
        max-width: 90%;
    }
    
    /* Center Input on Home Page */
    .hero-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh;
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

# --- PAGE LAYOUT LOGIC ---
if not st.session_state.messages:
    # --- HOME PAGE (Centered) ---
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown("<h1>THE RESERVE MEDICAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; letter-spacing: 2px; text-transform: uppercase; font-size: 0.9rem;'>AI-Powered Clinical Intelligence</p>", unsafe_allow_html=True)
    
    # Simple Centered Input
    with st.form("hero_form"):
        user_input = st.text_input("Describe your symptoms...", placeholder="Consult The Reserve Medical AI...", label_visibility="collapsed")
        submitted = st.form_submit_button("Start Consultation", use_container_width=True)
        if submitted and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- CHAT PAGE (Top Header + Bottom Input) ---
    st.markdown("<h1 style='font-size: 1.8rem; margin-top: 20px;'>THE RESERVE MEDICAL</h1>", unsafe_allow_html=True)
    
    # Display History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Bottom Input
    if prompt := st.chat_input("Continue consultation..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # Generate Response
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
