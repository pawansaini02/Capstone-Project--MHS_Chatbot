import os
import uuid
from datetime import datetime
import streamlit as st
# Assuming database.py exists and works if you uncomment sentiment lines
# from database import SentimentVectorDatabase
import google.generativeai as genai
from dotenv import load_dotenv
import random
import html # Import the html module for escaping

# Load environment variables from .env file
load_dotenv()

# --- Custom CSS Styling ---
def inject_custom_css():
    st.markdown("""
    <style>
        /* --- General --- */
        body {
            font-family: 'Arial', sans-serif;
        }
        .stApp {
            background: #EAF2F8;
            color: #34495E;
        }

        /* --- Headers and Text --- */
        h1, h2, h3, h4, h5, h6 {
            color: #2C3E50 !important;
            font-weight: 600;
        }
        p, li {
             color: #34495E !important;
        }

        /* --- Introduction Section --- */
        .intro-section {
            background: #FFFFFF;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            border: 1px solid #D6EAF8;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        .intro-section h2 {
            color: #3498DB !important;
            border-bottom: 2px solid #EAF2F8;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .intro-section h3 {
            color: #5DADE2 ;
            margin-top: 15px;
        }
        /* --- FIX: Style for buttons specifically in the intro section --- */
        .intro-section .stButton>button {
            background-color: #5DADE2 !important;
            color: white !important; /* Ensure text is white */
            border-radius: 8px;
            padding: 10px 20px;
            margin: 5px;
            border: none; /* Remove default border if any */
        }
        .intro-section .stButton>button:hover {
            background-color: #3498DB !important;
        }


        /* --- Chat Area --- */
        .stChatMessage {
            border-radius: 15px;
            padding: 1rem;
            margin: 0.8rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            border: 1px solid transparent;
        }
        [data-testid="stChatMessage"][aria-label="user"] {
            background: #D6EAF8;
            border-color: #AED6F1;
            color: #2C3E50 !important;
        }
        [data-testid="stChatMessage"][aria-label="user"] p { color: #2C3E50 !important; }

        [data-testid="stChatMessage"][aria-label="assistant"] {
            background: #FFFFFF;
            border-color: #EAECEE;
            color: #34495E !important;
        }
         [data-testid="stChatMessage"][aria-label="assistant"] p,
         [data-testid="stChatMessage"][aria-label="assistant"] li,
         [data-testid="stChatMessage"][aria-label="assistant"] strong {
             /* Ensure all elements inside assistant message inherit color */
             color: #34495E !important;
         }
         [data-testid="stChatMessage"][aria-label="assistant"] strong {
             /* Override for crisis text highlight */
             color: #E74C3C !important;
             font-weight: bold;
         }


        /* --- Input & Buttons --- */
        .stTextInput>div>div>input {
            color: #2C3E50 !important;
            background: #FFFFFF !important;
            border-radius: 8px;
            border: 1px solid #BDC3C7;
        }
        .stTextInput>div>div>input:focus {
             border-color: #5DADE2;
             box-shadow: 0 0 0 2px rgba(93, 173, 226, 0.2);
        }

        /* Quick response buttons (outside intro section) */
        div[data-testid="stHorizontalBlock"] .stButton>button { /* Target quick response buttons more specifically */
            width: 100%;
            margin: 4px 0;
            white-space: normal;
            height: auto;
            padding: 8px 12px;
            background: #5DADE2 !important;
            color: white !important;
            border: none;
            border-radius: 8px;
            transition: background-color 0.2s ease;
        }
        div[data-testid="stHorizontalBlock"] .stButton>button:hover {
            background-color: #3498DB !important;
        }
        div[data-testid="stHorizontalBlock"] .stButton>button:active {
            background-color: #2874A6 !important;
        }

       /* --- Sidebar --- */
        .stSidebar > div:first-child {
            background: #D4E6F1 !important;
            border-right: 1px solid #BDC3C7;
        }

        /* -------- Updated Section Below -------- */
        .stSidebar .sidebar-section {
            background: #3498DB !important;  /* Dark blue background */
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            color: white !important;  /* Base text color */
        }

        .stSidebar .sidebar-section *:not(a) {
            color: inherit !important;  /* Inherit from parent */
        }

        .stSidebar .sidebar-section h3 {
            color: white !important;
            margin-top: 0;
            padding-bottom: 5px;
            border-bottom: 1px solid rgba(255,255,255,0.3);
        }

        .stSidebar .sidebar-section a {
            color: #FFD700 !important;  /* Gold links */
            text-decoration: underline;
        }

        /* Updated button styles */
        .stSidebar .stButton>button {
            background: #1F618D !important;  /* Darker blue */
            color: white !important;
            border: 1px solid #154360 !important;
            width: 100%;
            margin: 10px 0;
        }

        .stSidebar .stButton>button:hover {
            background: #154360 !important;
            color: white !important;
        }
/* -------- End Updated Section -------- */

        /* --- Footer / Disclaimer styling --- */
        #disclaimer {
             margin-top: 30px;
             padding: 20px;
             background: #FEF9E7;
             border-radius: 10px;
             border: 1px solid #FAD7A0;
        }
        #disclaimer h3 {
             color: #B9770E !important;
             margin-top: 0;
        }
         /* --- FIX: Slightly darker text color for better contrast --- */
         #disclaimer p, #disclaimer li, #disclaimer strong {
             /* color: #7D6608 !important; OLD */
             color: #675406 !important; /* Darker yellow/brown */
             font-size: 0.95em;
         }
         #disclaimer strong { font-weight: bold; }


         /* Simple animation for bot response */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        [data-testid="stChatMessage"][aria-label="assistant"] {
            animation: fadeIn 0.5s ease-out;
        }

    </style>
    """, unsafe_allow_html=True)

class MentalHealthChatbot:
    def __init__(self):
        """Initialize the chatbot application."""
        if 'user_id' not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
            st.session_state.start_time = datetime.now()
        self.chatbot = self.initialize_chatbot()

    def initialize_chatbot(self):
        """Initialize and return the Gemini chatbot instance."""
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY:
            st.error("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.", icon="🚨")
            st.stop()
        try:
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash') # Or your preferred model
            # System instruction can be added here if needed:
            # system_instruction = "You are JeevaAI..."
            # return model.start_chat(system_instruction=system_instruction, history=[])
            return model.start_chat(history=[])
        except Exception as e:
            st.error(f"Error initializing Gemini model: {e}. Check API key/model name.", icon="🔥")
            st.stop()

    def process_user_message(self, message):
        """Process a user message and generate a response."""
        if not self.chatbot:
            return "Sorry, the chatbot is not available right now."
        try:
            crisis_keywords = [
                "suicide", "kill myself", "end my life", "want to die",
                "harm myself", "hurt myself", "don't want to live", "no reason to live",
                "overdose", "hopeless and want out"
            ]
            crisis_detected = any(keyword in message.lower() for keyword in crisis_keywords)

            response = self.chatbot.send_message(message)

            # Gracefully handle response structure
            if hasattr(response, "text") and response.text:
                 response_text = response.text
            elif hasattr(response, "parts") and response.parts:
                 response_text = "".join(part.text for part in response.parts if hasattr(part, "text"))
            else:
                 response_text = "I'm here to listen. Could you tell me a bit more about that?"
                 print(f"Warning: Unexpected response structure from Gemini for input: '{message}'")

            if crisis_detected:
                crisis_message = (
                    "\n\n"
                    "**🚨 Important:** It sounds like you're going through immense pain right now. "
                    "Please know that you're not alone and help is available. "
                    "Reaching out is a sign of strength. Here are some resources that can provide immediate support:\n"
                    "- **Emergency:** Call **911** (US/Canada) or your local emergency number immediately.\n"
                    "- **988 Suicide & Crisis Lifeline:** Call or text **988** (US).\n"
                    "- **Crisis Text Line:** Text **HOME** to **741741** (US/Canada), **85258** (UK).\n"
                    "- **Befrienders Worldwide:** Find a helpline in your country: [https://www.befrienders.org](https://www.befrienders.org)\n"
                    "**Please reach out to one of these resources now.**"
                )
                response_text = crisis_message + "\n\n" + response_text

            return response_text

        except Exception as e:
            st.error(f"An error occurred: {str(e)}", icon="⚠️")
            return ("I seem to be having a little trouble processing that right now. "
                   "Could you try rephrasing, or perhaps we could talk about something else?")

# --- Introduction and Disclaimer Content ---
def display_introduction():
    # --- FIX: Added unsafe_allow_html=True ---
    st.markdown("""
    <div class="intro-section">
        <h2>Supportive Conversations When You Need Them</h2>
        <p>
            Our AI companion, JeevaAI, is here to listen, support, and offer a gentle presence
            through difficult moments. While not a replacement for professional help,
            we aim to provide a compassionate space for you to express yourself and explore coping strategies.
        </p>

        
    </div>
    """, unsafe_allow_html=True) # <-- THIS IS THE FIX




def display_disclaimer():
    st.markdown('<a name="disclaimer"></a>', unsafe_allow_html=True) # Anchor for scrolling via URL
    # --- FIX: Added unsafe_allow_html=True ---
    st.markdown("""
    <div id="disclaimer">
        <h3>Important Disclaimer</h3>
        <p>
            <strong>JeevaAI is an AI chatbot and not a substitute for professional mental health care, diagnosis, or treatment.</strong>
            It cannot provide medical advice or crisis intervention.
        </p>
        <p>
            <strong>If you are experiencing a crisis or emergency:</strong>
        </p>
        <ul>
            <li>Please call your local emergency number (like <strong>112</strong> in the India) immediately.</li>
            <li>Contact a mental health professional.</li>
            <li>Find international helplines via <strong>Befrienders Worldwide</strong>.</li>
        </ul>
        <p>
            Your conversations here are intended for general support and exploration. Please prioritize professional help for serious concerns.
        </p>
    </div>
    """, unsafe_allow_html=True) # <-- THIS IS THE FIX


# --- Main Application ---
def main():
    st.set_page_config(
        page_title="JeevaAI - Mental Health Support",
        page_icon="🧠",
        layout="centered"
    )

    inject_custom_css() # Apply styling

    # --- Header ---
    st.markdown("""
        <div style="text-align: center; margin-bottom: 10px;">
             <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" alt="JeevaAI Logo" width="70">
             <h1 style="margin-bottom: 0; color: #2C3E50;">JeevaAI</h1>
             <h3 style="margin-top: 5px; color: #5DADE2;">Your Compassionate Mental Wellness Companion</h3>
        </div>
    """, unsafe_allow_html=True)

    # --- Introduction Section ---
    display_introduction()

    # --- Initialize Chatbot ---
    if 'chatbot_instance' not in st.session_state:
        with st.spinner("🌟 Preparing your supportive space..."):
            st.session_state.chatbot_instance = MentalHealthChatbot()
        if 'messages' not in st.session_state:
            # Initial message setup
             st.session_state.messages = [{
                "role": "assistant",
                "content": """
                <div style='padding: 10px; border-radius: 15px;'>
                    <p>Hello there! I'm JeevaAI, ready to listen whenever you'd like to share.
                    How are you feeling today? Remember to check the information above if this is your first time here.</p>
                    <div style='text-align: center; margin-top: 10px;'>🌱</div>
                </div>
                """,
                "is_html": True # Flag this as HTML content
            }]


    # --- Display Chat Messages ---
    for message in st.session_state.messages:
        avatar_url = "https://cdn-icons-png.flaticon.com/512/1144/1144760.png" if message["role"] == "user" else "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
        with st.chat_message(message["role"], avatar=avatar_url):
            # --- FIX: Check the 'is_html' flag before rendering ---
            if message.get("is_html", False): # Default to False if key missing
                st.markdown(message["content"], unsafe_allow_html=True)
            else:
                # Render as plain markdown (safer default for user input or non-HTML bot responses)
                st.markdown(message["content"])

    # --- Quick Responses ---
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        st.markdown("<div style='text-align: center; margin: 15px 0; color: #5DADE2; font-weight: bold;'>Quick Chat Starters:</div>", unsafe_allow_html=True)
        quick_responses = [
            "I'm feeling a bit stressed lately.",
            "Can we talk about managing anxiety?",
            "I just need someone to listen.",
            "Suggest a simple mindfulness exercise."
        ]
        cols = st.columns(len(quick_responses))
        for i, response in enumerate(quick_responses):
            if cols[i].button(response, key=f"quick_{i}"):
                st.session_state.messages.append({"role": "user", "content": response})
                with st.spinner("JeevaAI is thinking..."):
                    bot_response_text = st.session_state.chatbot_instance.process_user_message(response)

                    # --- FIX: Escape AI response text before adding custom HTML ---
                    safe_response_html = html.escape(bot_response_text).replace('\n', '<br/>')
                    emoji_html = f"""<div style='text-align: center; margin-top: 15px;'>
                                        {random.choice(['🌸', '🧘‍♀️', '☕', '✨', '🌱'])}
                                    </div>"""
                    formatted_response = f"""
                    <div style='padding: 10px; border-radius: 15px;'>
                        <p>{safe_response_html}</p>
                        {emoji_html}
                    </div>
                    """
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": formatted_response,
                        "is_html": True # Flag as HTML
                    })
                st.rerun()

    # --- User Input Field ---
    if user_input := st.chat_input("Share your thoughts or feelings here..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("JeevaAI is listening and reflecting..."):
            response_text = st.session_state.chatbot_instance.process_user_message(user_input)

             # --- FIX: Escape AI response text before adding custom HTML ---
            safe_response_html = html.escape(response_text).replace('\n', '<br/>')
            emoji_html = f"""<div style='text-align: center; margin-top: 15px;'>
                                 {random.choice(['💬', '👂', '💖', '🤝', '💡'])}
                             </div>"""
            formatted_response = f"""
            <div style='padding: 10px; border-radius: 15px;'>
                <p>{safe_response_html}</p>
                {emoji_html}
            </div>
            """
            st.session_state.messages.append({
                "role": "assistant",
                "content": formatted_response,
                "is_html": True # Flag as HTML
            })
        st.rerun()

    # --- Sidebar Content ---
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            """
            <div class="sidebar-section">
                <h3>🆘 Crisis Support</h3>
                <p><strong>If you are in immediate danger, please call your local emergency services.</strong></p>
                <ul>
                    <li><b>India:</b> 1800-599-0019 (Vandrevala Fdn)</li>
                    <li><b>US/Canada:</b> Call or text 988</li>
                    <li><b>UK:</b> Call 111</li>
                    <li><b>Int'l:</b> Find a helpline via <a href="https://findahelpline.com/" target="_blank">Find A Helpline</a> or <a href="https://www.befrienders.org/" target="_blank">Befrienders Worldwide</a></li>
                 </ul>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(
            """
            <div class="sidebar-section">
                <h3>💡 Wellness Tips</h3>
                <p>Remember to:</p>
                <ul>
                    <li>Stay hydrated.</li>
                    <li>Take short breaks.</li>
                    <li>Practice mindful breathing.</li>
                    <li>Connect with loved ones.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🔄 Start New Chat Session", key="new_chat_sidebar", use_container_width=True):
             st.session_state.messages = [{
                "role": "assistant",
                "content": """
                <div style='padding: 10px; border-radius: 15px;'>
                    <p>Starting fresh! I'm here and ready to listen. What's on your mind?</p>
                    <div style='text-align: center; margin-top: 10px;'>✨</div>
                </div>
                """,
                "is_html": True
            }]
             # Optionally reset Gemini history if needed/possible
             # st.session_state.chatbot_instance.chatbot.history.clear()
             st.toast("New chat session started!", icon="✅")
             st.rerun()

    # --- Disclaimer Section (at the bottom) ---
    display_disclaimer() # Ensure this is called to display it


if __name__ == "__main__":
    main()