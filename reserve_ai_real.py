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

# --- CUSTOM CSS (Stabilized) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

    /* Global Reset */
    .stApp {
        background-color: #FAF7F2 !important;
        font-family: 'Inter', sans-serif !important;
        color: #2C2C2C !important;
    }
    
    /* Remove Sidebar & Decorations */
    section[data-testid="stSidebar"] { display: none; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Centered Header */
    h1 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #1A1A1A !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-size: 2.2rem !important;
        text-align: center !important;
        margin-top: 20px !important;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #666;
        text-align: center;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 40px;
    }

    /* Message Container */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 10px 0 !important;
    }

    /* Remove Avatars */
    .stChatMessageAvatar { display: none !important; }

    /* User Message (Right Aligned Bubble) */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        flex-direction: row-reverse;
    }
    div[data-testid="stChatMessage"]:nth-child(odd) > div:first-child {
        background-color: #E8E0D4;
        color: #2C2C2C;
        padding: 12px 20px;
        border-radius: 20px 20px 0 20px;
        text-align: left;
        max-width: 80%;
        margin-left: auto !important; /* Force Right */
        margin-right: 0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* AI Message (Left Aligned Text) */
    div[data-testid="stChatMessage"]:nth-child(even) {
        flex-direction: row;
    }
    div[data-testid="stChatMessage"]:nth-child(even) > div:first-child {
        background-color: transparent;
        color: #2C2C2C;
        padding: 0;
        text-align: left;
        max-width: 90%;
        margin-right: auto !important; /* Force Left */
        margin-left: 0 !important;
    }

    /* Input Box (Floating Bottom) */
    .stChatInput {
        position: fixed;
        bottom: 30px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 100%;
        max-width: 700px; /* Match layout width */
        z-index: 1000;
    }
    
    .stChatInputContainer {
        border-radius: 30px !important;
        border: 1px solid #D0D0D0 !important;
        background-color: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }

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

# --- HEADER DISPLAY ---
# Keep it simple: Always at the top. This prevents layout jumping.
st.markdown("<h1>THE RESERVE MEDICAL</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>AI-Powered Clinical Intelligence</p>", unsafe_allow_html=True)

# --- CHAT HISTORY ---
# Create a container so messages don't get hidden behind the fixed input
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True) # Spacer

# --- INPUT AREA ---
if prompt := st.chat_input("Consult The Reserve..."):
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # AI Response
    with chat_container:
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
