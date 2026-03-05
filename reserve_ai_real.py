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

# --- THEME COLORS (Claude Dark Mode) ---
BG_COLOR = "#1A1A1A"        # Deep Charcoal
USER_BUBBLE = "#2E2E2E"     # Soft Dark Grey
TEXT_COLOR = "#E5E5E5"      # Muted White
ACCENT_COLOR = "#D9D9D9"    # Subtle Accent
INPUT_BG = "#2E2E2E"        # Input Field Background

# --- CUSTOM CSS (Minimalist Dark) ---
st.markdown(f"""
<style>
    /* Import Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* Global App Background */
    .stApp {{
        background-color: {BG_COLOR};
        font-family: 'Inter', sans-serif;
        color: {TEXT_COLOR};
    }}

    /* Headers */
    h1 {{
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: {TEXT_COLOR};
        text-align: center;
        font-size: 1.5rem;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }}
    
    .subtitle {{
        font-family: 'Inter', sans-serif;
        color: #888;
        text-align: center;
        font-size: 0.9rem;
        font-weight: 400;
        margin-bottom: 40px;
    }}

    /* Chat Container */
    .chat-container {{
        max-width: 700px;
        margin: auto;
        padding-bottom: 100px; /* Space for input */
    }}

    /* User Message (Rounded Pill) */
    .user-msg {{
        background-color: {USER_BUBBLE};
        color: {TEXT_COLOR};
        padding: 12px 20px;
        border-radius: 20px;
        align-self: flex-end;
        max-width: 80%;
        font-size: 1rem;
        line-height: 1.5;
        margin-left: auto;
        margin-bottom: 20px;
        display: inline-block;
        float: right;
        clear: both;
    }}

    /* AI Message (Clean Text, No Bubble) */
    .ai-msg {{
        background-color: transparent;
        color: {TEXT_COLOR};
        padding: 10px 0;
        align-self: flex-start;
        max-width: 100%;
        font-size: 1rem;
        line-height: 1.6;
        margin-right: auto;
        margin-bottom: 30px;
        float: left;
        clear: both;
        width: 100%;
    }}
    
    /* Markdown Headers in AI Text */
    .ai-msg strong {{
        color: white;
        font-weight: 600;
    }}

    /* Input Bar (Fixed Bottom) */
    .stTextInput > div > div > input {{
        background-color: {INPUT_BG};
        color: {TEXT_COLOR};
        border: 1px solid #444;
        border-radius: 12px;
        padding: 12px 15px;
        font-family: 'Inter', sans-serif;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: #666;
        box-shadow: none;
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1>The Reserve Medical</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>AI Healthcare Assistant</p>", unsafe_allow_html=True)

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
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# --- CHAT DISPLAY ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            # AI Message (Clean Text)
            st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)

# --- INPUT AREA ---
# Create a placeholder for the stream
stream_placeholder = st.empty()

if prompt := st.chat_input("Message The Reserve Medical..."):
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user-msg">{prompt}</div>', unsafe_allow_html=True)

    # 2. STREAM AI RESPONSE
    full_response = ""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Call OpenAI with STREAM=TRUE
        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            # Process the stream chunk by chunk
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    # Typewriter Effect
                    message_placeholder.markdown(full_response + "▌")
            
            # Finalize (remove cursor)
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Error: {e}")

    # 3. Save to History
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Rerun to clear input box cleanly (optional, but st.chat_input handles it mostly)
    # st.rerun()
