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

# --- THEME COLORS ---
NAVY_BLUE = "#012161"
CREAM_BG = "#F5F5F0"
WHITE_CARD = "#FFFFFF"
TEXT_DARK = "#333333"

# --- CUSTOM CSS (Luxury Navy Theme) ---
st.markdown(f"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Source+Sans+Pro:wght@400;600&display=swap');

    /* Global App Background */
    .stApp {{
        background: linear-gradient(135deg, #E0E0E0 0%, #F5F5F0 100%);
        font-family: 'Source Sans Pro', sans-serif;
        color: {TEXT_DARK};
    }}

    /* Headers (Luxury Serif) */
    h1, h2, h3 {{
        font-family: 'Playfair Display', serif;
        color: {NAVY_BLUE};
        text-align: center;
    }}
    
    /* Subtitle Styling */
    .subtitle {{
        font-family: 'Source Sans Pro', sans-serif;
        color: #666;
        text-align: center;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-size: 0.9em;
        margin-top: -15px;
        margin-bottom: 30px;
    }}

    /* Chat Container (Card Effect) */
    .chat-container {{
        max-width: 600px;
        margin: auto;
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 15px;
    }}

    /* User Message (Navy Blue) */
    .user-msg {{
        background-color: {NAVY_BLUE};
        color: white;
        padding: 14px 20px;
        border-radius: 20px 20px 0 20px;
        align-self: flex-end;
        max-width: 85%;
        box-shadow: 0 4px 10px rgba(1, 33, 97, 0.2);
        font-size: 16px;
        margin-left: auto; /* Force right */
        margin-bottom: 10px;
    }}

    /* AI Message (Clean White Card) */
    .ai-msg {{
        background-color: {WHITE_CARD};
        color: {TEXT_DARK};
        padding: 18px 25px;
        border-radius: 20px 20px 20px 0;
        align-self: flex-start;
        max-width: 90%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 5px solid {NAVY_BLUE};
        font-size: 16px;
        line-height: 1.6;
        margin-right: auto; /* Force left */
        margin-bottom: 10px;
    }}

    /* Input Field Styling */
    div[data-testid="stForm"] {{
        border: none;
        box-shadow: none;
        background: transparent;
    }}
    
    .stTextInput > div > div > input {{
        border-radius: 30px;
        padding: 10px 20px;
        border: 1px solid #ccc;
    }}

    /* Button Styling */
    .stButton > button {{
        background-color: {NAVY_BLUE};
        color: white;
        border-radius: 30px;
        padding: 10px 30px;
        font-weight: 600;
        border: none;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .stButton > button:hover {{
        background-color: #011a4d;
        color: white;
    }}

    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1>The Reserve Medical</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>AI Healthcare</p>", unsafe_allow_html=True)

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

# --- CHAT HISTORY ---
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

st.markdown('<p style="text-align: center; font-size: 0.8em; color: #888; margin-top: 30px;">⚠️ Educational use only. Consult a physician for medical advice.</p>', unsafe_allow_html=True)
