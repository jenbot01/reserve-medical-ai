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
NAVY = "#012161"
GOLD = "#C5A059"
CREAM_BG = "#FAFAF9"
TEXT_DARK = "#1A1A1A"

# --- CUSTOM CSS (Ultra-Luxury) ---
st.markdown(f"""
<style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Jost:wght@300;400;500&display=swap');

    /* App Background */
    .stApp {{
        background-color: {CREAM_BG};
        font-family: 'Jost', sans-serif;
        color: {TEXT_DARK};
    }}

    /* Headers (Cormorant Garamond) */
    h1 {{
        font-family: 'Cormorant Garamond', serif;
        color: {NAVY};
        text-align: center;
        font-size: 3rem !important;
        font-weight: 700;
        margin-bottom: 0px;
    }}
    
    .subtitle {{
        font-family: 'Jost', sans-serif;
        color: {GOLD};
        text-align: center;
        letter-spacing: 4px;
        text-transform: uppercase;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: -10px;
        margin-bottom: 40px;
    }}

    /* Chat Container */
    .chat-container {{
        max-width: 650px;
        margin: auto;
        padding: 0 10px;
        display: flex;
        flex-direction: column;
        gap: 25px; /* More breathing room */
    }}

    /* User Message (Minimalist Block) */
    .user-msg {{
        background-color: {NAVY};
        color: white;
        padding: 15px 25px;
        border-radius: 4px; /* Sharp corners = Expensive */
        align-self: flex-end;
        max-width: 80%;
        font-family: 'Jost', sans-serif;
        font-weight: 400;
        box-shadow: 0 4px 15px rgba(1, 33, 97, 0.15);
        border-bottom: 2px solid {GOLD}; /* Gold detail */
        margin-left: auto;
    }}

    /* AI Message (The "Medical Report" Card) */
    .ai-msg {{
        background-color: white;
        color: {TEXT_DARK};
        padding: 30px;
        border-radius: 2px;
        align-self: flex-start;
        width: 100%; /* Full width for authority */
        box-shadow: 0 5px 20px rgba(0,0,0,0.03);
        border-top: 3px solid {GOLD}; /* Top Gold Line */
        font-family: 'Jost', sans-serif;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-right: auto;
    }}

    /* Markdown Styling inside AI Card */
    .ai-msg strong {{
        color: {NAVY};
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.2rem;
        font-weight: 700;
    }}

    /* Input Field (Clean Line) */
    .stTextInput > div > div > input {{
        background-color: transparent;
        border: none;
        border-bottom: 2px solid {NAVY};
        border-radius: 0;
        padding: 10px 5px;
        color: {NAVY};
        font-family: 'Jost', sans-serif;
        font-size: 1rem;
    }}
    .stTextInput > div > div > input:focus {{
        border-bottom: 2px solid {GOLD};
        box-shadow: none;
    }}

    /* Button (Gold Luxury) */
    .stButton > button {{
        background-color: {NAVY};
        color: {GOLD};
        border: 1px solid {NAVY};
        border-radius: 0;
        padding: 12px 40px;
        font-family: 'Jost', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.8rem;
        transition: all 0.3s ease;
        width: 100%;
    }}
    .stButton > button:hover {{
        background-color: {GOLD};
        color: {NAVY};
        border-color: {GOLD};
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
    user_input = st.text_input("Consult with The Reserve AI...", key="input")
    submit_button = st.form_submit_button(label='Submit Inquiry')

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

st.markdown('<p style="text-align: center; font-size: 0.7em; color: #aaa; margin-top: 40px; font-family: Jost;">THE RESERVE MEDICAL &copy; 2026</p>', unsafe_allow_html=True)
