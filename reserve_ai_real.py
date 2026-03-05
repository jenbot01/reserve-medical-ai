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

    /* Remove Sidebar & Branding */
    section[data-testid="stSidebar"] { display: none; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* GLOBAL: Remove Avatars */
    .stChatMessageAvatar { display: none !important; }
    div[data-testid="stChatMessage"] > div:first-child { display: none !important; } /* Double Kill */

    /* GLOBAL: Message Alignment */
    div[data-testid="stChatMessage"] {
        padding: 0.5rem 0;
        background-color: transparent !important;
        border: none !important;
        width: 100%;
    }

    /* USER (Right Aligned Bubble) */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        flex-direction: row-reverse;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) .stMarkdown {
        background-color: #E8E0D4;
        color: #2C2C2C;
        padding: 12px 20px;
        border-radius: 20px 20px 0 20px;
        text-align: left;
        max-width: 80%;
        margin-left: auto !important; /* Push to Right */
        margin-right: 0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        float: right; /* Force float */
        clear: both;
    }

    /* AI (Left Aligned Text) */
    div[data-testid="stChatMessage"]:nth-child(even) {
        flex-direction: row;
    }
    div[data-testid="stChatMessage"]:nth-child(even) .stMarkdown {
        background-color: transparent;
        padding: 0;
        text-align: left;
        max-width: 90%;
        margin-right: auto !important; /* Push to Left */
        margin-left: 0 !important;
        float: left; /* Force float */
        clear: both;
    }

    /* HOME PAGE: Centered Input */
    .hero-input input {
        text-align: center;
        border-radius: 30px;
        padding: 15px;
        border: 1px solid #ccc;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    /* CHAT PAGE: Bottom Input */
    .stChatInput { bottom: 30px !important; }

</style>
""", unsafe_allow_html=True)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are The Reserve Medical Assistant.
TONE: Professional, warm, authoritative.
FORMAT: No numbers. Bold the **Condition Name** only.

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
    # HERO MODE (Center)
    st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True) # Spacer
    st.markdown("<h1 style='text-align: center; font-family: Cormorant Garamond; font-size: 3rem; margin-bottom: 10px;'>THE RESERVE MEDICAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-family: Inter; color: #666; letter-spacing: 2px; text-transform: uppercase;'>AI-Powered Clinical Intelligence</p>", unsafe_allow_html=True)
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True) # Spacer

    # CENTER INPUT
    with st.form("hero_form"):
        user_input = st.text_input("Describe your symptoms...", key="hero_input", label_visibility="collapsed")
        submitted = st.form_submit_button("Consult", use_container_width=True)
        
        if submitted and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

else:
    # CHAT MODE (Top Header)
    st.markdown("<h1 style='text-align: center; font-family: Cormorant Garamond; font-size: 1.5rem; margin-top: 10px; margin-bottom: 20px;'>THE RESERVE MEDICAL</h1>", unsafe_allow_html=True)
    
    # HISTORY
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # BOTTOM INPUT
    if prompt := st.chat_input("Continue consultation..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # GENERATE RESPONSE (After Rerun)
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
