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

# --- CSS (Nuclear Option) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

    .stApp { background-color: #FAF7F2 !important; font-family: 'Inter', sans-serif !important; color: #2C2C2C !important; }

    /* Hide Streamlit Cruft */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Header (Center) */
    .header-center {
        text-align: center; margin-top: 20px;
    }
    .header-center h1 {
        font-family: 'Cormorant Garamond', serif; font-size: 2.5rem; color: #1A1A1A; margin-bottom: 5px;
    }
    .header-center p {
        font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #666; letter-spacing: 2px; text-transform: uppercase;
    }

    /* Message Container */
    .chat-container {
        display: flex; flex-direction: column; gap: 20px; margin-bottom: 100px;
    }

    /* User Bubble (Right) */
    .user-msg {
        align-self: flex-end;
        background-color: #E8E0D4;
        color: #2C2C2C;
        padding: 12px 20px;
        border-radius: 20px 20px 0 20px;
        max-width: 80%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-left: auto; /* Force Right */
    }

    /* AI Text (Left) */
    .ai-msg {
        align-self: flex-start;
        background-color: transparent;
        color: #2C2C2C;
        padding: 0;
        max-width: 90%;
        font-size: 1rem;
        line-height: 1.6;
        margin-right: auto; /* Force Left */
    }

    /* Input Box (Fixed Bottom) */
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

# --- RENDER MESSAGES (Raw HTML) ---
if st.session_state.messages:
    # Small Header (Top)
    st.markdown("""
    <div class="header-center" style="margin-top: 0; margin-bottom: 30px;">
        <h1 style="font-size: 1.5rem;">THE RESERVE MEDICAL</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat History
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role_class = "user-msg" if msg["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # HERO MODE (Center)
    st.markdown("""
    <div style="height: 20vh;"></div>
    <div class="header-center">
        <h1>THE RESERVE MEDICAL</h1>
        <p>AI-Powered Clinical Intelligence</p>
    </div>
    <div style="height: 40px;"></div>
    """, unsafe_allow_html=True)
    
    # Input in Center (Using Form)
    with st.form("hero_form"):
        user_input = st.text_input("Describe your symptoms...", key="hero_input", label_visibility="collapsed")
        submitted = st.form_submit_button("Start Consultation", use_container_width=True)
        if submitted and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun()

# --- BOTTOM INPUT (Only show if chatting) ---
if st.session_state.messages:
    if prompt := st.chat_input("Continue consultation..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# --- GENERATE RESPONSE (After Rerun) ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    # Stream Response (Using Placeholder)
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
                # Update Placeholder with HTML (To keep styling consistent)
                # Note: Streaming HTML is tricky, so we stream text inside a styled div
                message_placeholder.markdown(f'<div class="ai-msg">{full_response}▌</div>', unsafe_allow_html=True)
        
        # Finalize
        message_placeholder.markdown(f'<div class="ai-msg">{full_response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"Error: {e}")
