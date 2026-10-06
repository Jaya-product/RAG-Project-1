# Override sqlite3 for Streamlit Cloud deployment (ChromaDB requirement)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import sys
import os
import uuid

# Ensure the scripts directory is in the path so we can import llm_logic
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, 'scripts'))

try:
    from llm_logic import generate_response
except ImportError:
    st.error("Failed to load backend logic. Ensure 'scripts/llm_logic.py' exists.")
    st.stop()

# 1. UI Layout & Title
st.set_page_config(page_title="NutriGuide | AI Nutrition Assistant", page_icon="🥗", layout="centered")

# Custom CSS for a clean, modern aesthetic & hiding Streamlit UI
st.markdown("""
<style>
    /* Hide Streamlit default UI (Deploy, Menu, Footer) */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stDeployButton"] {display: none !important;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stAppDeployButton"] {display: none !important;}
    
    /* Ensure the native sidebar toggle remains fully visible */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        z-index: 99999 !important;
    }

    .stApp {
        background-color: #FAFAFA;
    }
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #E0E0E0;
        background-color: #FFFFFF;
        color: #333333;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        border-color: #4CAF50;
        color: #4CAF50;
        background-color: #F9F9F9;
    }
    .main-header {
        text-align: center;
        margin-bottom: 5px;
        color: #2E7D32;
    }
    .sub-header {
        text-align: center;
        color: #666666;
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    .disclaimer {
        text-align: center;
        font-size: 0.85em;
        color: #999999;
        margin-bottom: 30px;
    }
    .welcome-text {
        text-align: center; 
        color: #444; 
        font-size: 1.2em;
        font-weight: 500;
        margin-bottom: 20px;
    }
    .suggestion-text {
        font-size: 0.9em;
        color: #555555;
        margin-bottom: 10px;
        font-weight: 500;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 2. Session State Management
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

def get_current_messages():
    if not st.session_state.current_session_id:
        return []
    for s in st.session_state.chat_sessions:
        if s["id"] == st.session_state.current_session_id:
            return s["messages"]
    return []

def add_message(role, content):
    if not st.session_state.current_session_id:
        # Create new session
        new_id = str(uuid.uuid4())
        title = content[:40] + "..." if len(content) > 40 else content
        st.session_state.chat_sessions.insert(0, {"id": new_id, "title": title, "messages": []})
        st.session_state.current_session_id = new_id
    
    for s in st.session_state.chat_sessions:
        if s["id"] == st.session_state.current_session_id:
            s["messages"].append({"role": role, "content": content})
            break

# Sidebar logic moved to the bottom of the script to ensure state updates reflect immediately.

current_messages = get_current_messages()

# Main Area Headers (Only show if no chat history exists in current session)
if not current_messages:
    st.markdown("<h1 class='main-header'>🥗 NutriGuide</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Your AI guide for food, nutrition & healthy choices</p>", unsafe_allow_html=True)
    st.markdown("<p class='disclaimer'>For general nutrition and food-safety information. Not a substitute for personalized medical advice.</p>", unsafe_allow_html=True)
    st.markdown("<p class='welcome-text'>Hi! What would you like to know about food or nutrition today?</p>", unsafe_allow_html=True)
    
    # Suggested Questions
    st.markdown("<p class='suggestion-text'>Try asking:</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    def set_suggestion(text):
        st.session_state.suggestion = text
        
    with col1:
        st.button("🥗 What does a balanced diet look like?", on_click=set_suggestion, args=("What does a balanced diet look like?",), use_container_width=True)
        st.button("🥩 What are good sources of protein?", on_click=set_suggestion, args=("What are good sources of protein?",), use_container_width=True)
        st.button("🥛 What are good sources of calcium?", on_click=set_suggestion, args=("What are good sources of calcium?",), use_container_width=True)
    
    with col2:
        st.button("🍌 Is eating bananas every day healthy?", on_click=set_suggestion, args=("Is eating bananas every day healthy?",), use_container_width=True)
        st.button("❄️ How long can I safely freeze meat?", on_click=set_suggestion, args=("How long can I safely freeze meat?",), use_container_width=True)
        st.button("🍎 How many fruits should I eat daily?", on_click=set_suggestion, args=("How many fruits should I eat daily?",), use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True) # some spacing before input

# 3. Display Historical Messages
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4 & 5. Chat Interface & Backend Connection
prompt = st.chat_input("Ask me anything about food, nutrition or food safety...")

if "suggestion" in st.session_state and st.session_state.suggestion:
    prompt = st.session_state.suggestion
    st.session_state.suggestion = None

if prompt:
    # Append user message to state and display
    add_message("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # 6. Error Handling during Generation
    with st.chat_message("assistant"):
        with st.spinner("Finding information..."):
            try:
                # 7. Call Phase 5 Backend (Top-K and Chunk Size are strictly handled there)
                response_text = generate_response(prompt)
                
                # Display structured backend response
                st.markdown(response_text)
                
                # Append assistant response to state
                add_message("assistant", response_text)
                
            except Exception as e:
                error_msg = f"**I'm sorry, I ran into an issue:** {str(e)}\n\nPlease try again."
                st.error(error_msg)
                # We do not append the error to session state so the user can easily retry

# Render Sidebar at the end so it captures any newly created sessions
with st.sidebar:
    st.markdown("### 🥗 NutriGuide")
    st.markdown("---")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_session_id = None
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Recent Chats**")
    
    if not st.session_state.chat_sessions:
        st.markdown("<p style='color: #888; font-size: 0.9em;'>No recent chats yet</p>", unsafe_allow_html=True)
    else:
        for session in st.session_state.chat_sessions[:10]:
            if st.button(f"• {session['title']}", key=f"session_{session['id']}", use_container_width=True):
                st.session_state.current_session_id = session['id']
                st.rerun()
                
    st.markdown("---")
    
    if st.button("🗑️ Clear chat history", use_container_width=True):
        st.session_state.chat_sessions = []
        st.session_state.current_session_id = None
        st.rerun()
