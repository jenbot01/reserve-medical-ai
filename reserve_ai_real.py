import streamlit as st
import os
from openai import OpenAI

# --- CONFIGURATION ---
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ OpenAI API Key not found! Please add it to Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(page_title="Reserve Medical", page_icon="🩺", layout="centered")

# --- THEME COLORS ---
BG_COLOR = "#D1C7BD"       # Warm Beige
TEXT_COLOR = "#322d29"     # Deep Charcoal
ACCENT_COLOR = "#72383D"   # Burgundy
USER_BUBBLE = "#72383D"    # Burgundy (User)
AI_BUBBLE = "#EFE9E1"      # Light Cream (AI)

# --- CUSTOM CSS (Luxurious & Readable) ---
st.markdown(f"""
<style>
    /* Global Background */
    .stApp {{
        background-color: {BG_COLOR};
        color: {TEXT_COLOR};
        font-family: 'Helvetica Neue', sans-serif;
    }}
    
    /* Headers (Serif for Luxury) */
    h1, h2, h3 {{
        font-family: 'Georgia', serif;
        color: {TEXT_COLOR};
        font-weight: normal;
    }}
    
    /* Chat Container */
    .chat-container {{
        max-width: 600px;
        margin: auto;
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 15px;
    }}
    
    /* User Message Bubble */
    .user-msg {{
        background-color: {USER_BUBBLE};
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 0 18px;
        align-self: flex-end;
        max-width: 85%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        font-size: 16px;
        line-height: 1.5;
        margin-left: auto; /* Force right align */
        margin-bottom: 10px;
    }}
    
    /* AI Message Bubble */
    .ai-msg {{
        background-color: {AI_BUBBLE};
        color: {TEXT_COLOR};
        padding: 15px 20px;
        border-radius: 18px 18px 18px 0;
        align-self: flex-start;
        max-width: 90%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        font-size: 16px;
        line-height: 1.6;
        border-left: 4px solid {ACCENT_COLOR}; /* Premium accent line */
        margin-right: auto; /* Force left align */
        margin-bottom: 10px;
    }}
    
    /* Input Field Styling */
    .stTextInput > div > div > input {{
        background-color: #EFE9E1;
        color: {TEXT_COLOR};
        border: 1px solid {ACCENT_COLOR};
        border-radius: 10px;
    }}
    
    /* Button Styling */
    .stButton > button {{
        background-color: {ACCENT_COLOR};
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>The Reserve Medical</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #555;'>Private. Premium. Personal.</p>", unsafe_allow_html=True)

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

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# --- CHAT DISPLAY ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        role_class = "user-msg" if msg["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- INPUT AREA ---
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("Describe your symptoms...", key="input")
    submit_button = st.form_submit_button(label='Consult AI')

if submit_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        ai_reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown('<p style="text-align: center; font-size: 0.8em; color: #555; margin-top: 20px;">⚠️ Educational use only. Consult a physician for medical advice.</p>', unsafe_allow_html=True)
