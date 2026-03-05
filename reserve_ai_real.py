import streamlit as st
import os
import time
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
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

    /* Global Background */
    .stApp {
        background-color: #FAF7F2 !important;
        font-family: 'Inter', sans-serif !important;
        color: #2C2C2C !important;
    }

    /* Headers (Force Cormorant Garamond) */
    h1, h2, h3 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #1A1A1A !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* Chat Messages Container */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
    }

    /* User Message (Beige Pill) */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        flex-direction: row-reverse;
        text-align: right;
        background-color: transparent;
    }
    
    div[data-testid="stChatMessage"]:nth-child(odd) .stMarkdown {
        background-color: #E8E0D4;
        color: #2C2C2C;
        padding: 12px 20px;
        border-radius: 20px;
        display: inline-block;
        max-width: 80%;
        text-align: left; /* Keep text readable */
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* AI Message (Clean Text) */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: transparent;
    }
    
    div[data-testid="stChatMessage"]:nth-child(even) .stMarkdown {
        background-color: transparent;
        padding: 10px 0;
        color: #2C2C2C;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        font-size: 1.05rem;
    }

    /* Input Box Styling (Floating Card) */
    .stChatInput {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 700px;
        z-index: 999;
    }
    
    .stChatInputContainer {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 24px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
        padding: 5px 10px !important;
    }
    
    .stChatInput textarea {
        background-color: transparent !important;
        color: #2C2C2C !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* EKG Animation (Heartbeat) */
    @keyframes heartbeat {
        0% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(1); opacity: 0.5; }
    }
    .ekg-loader {
        width: 10px;
        height: 10px;
        background-color: #C5A059; /* Gold Dot */
        border-radius: 50%;
        margin: 10px 0;
        animation: heartbeat 1s infinite;
        display: inline-block;
    }

    /* Hide Default Avatars */
    .stChatMessageAvatar {
        display: none !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 style='text-align: center; margin-top: 40px;'>The Reserve Medical</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-family: Inter; color: #888; margin-bottom: 60px;'>AI Healthcare Assistant</p>", unsafe_allow_html=True)

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

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CHAT DISPLAY ---
for msg in st.session_state.messages:
    role = msg["role"]
    with st.chat_message(role):
        st.markdown(msg["content"])

# --- INPUT AREA ---
if prompt := st.chat_input("Message The Reserve Medical..."):
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Response with Streaming & EKG
    with st.chat_message("assistant"):
        # EKG Loader
        loader_placeholder = st.empty()
        loader_placeholder.markdown('<div class="ekg-loader"></div> <span style="font-family:Inter; color:#888; font-size:0.8em;">Analyzing...</span>', unsafe_allow_html=True)
        
        # Artificial "Thinking" Pause (to show off the EKG)
        time.sleep(1.5)
        
        # Clear loader
        loader_placeholder.empty()
        
        # Stream Response
        message_placeholder = st.empty()
        full_response = ""
        
        # Build Context (System Prompt + History)
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
