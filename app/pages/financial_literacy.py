import streamlit as st
from app.pages import fl_config
from app import finance_app_main

# Hides the default sidebar
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .block-container {
            padding-left: 6rem;
            padding-right: 2rem;
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Finance Learning Path",
    page_icon="💸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- HIDE DEFAULT STREAMLIT UI ---
hide_default_format = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_default_format, unsafe_allow_html=True)

# --- INITIAL SESSION STATE ---
if "username" not in st.session_state:
    st.session_state.username = "Lohith"

if "language" not in st.session_state:
    st.session_state.language = "English"

if "completed_topics" not in st.session_state:
    st.session_state.completed_topics = []

# --- MAIN HEADER (Welcome first, then language selection) ---
t = fl_config.translations[st.session_state.language]

# Welcome message first
st.markdown(f"### {t['welcome']}, **{st.session_state.username}!**")
st.caption(t["caption"])

# --- LANGUAGE SELECTION (auto refresh when changed) ---
prev_lang = st.session_state.language
st.markdown(f"### {fl_config.translations[prev_lang]['choose_language']}")

language = st.selectbox(
    "",
    options=list(fl_config.translations.keys()),
    index=list(fl_config.translations.keys()).index(prev_lang),
    key="language_selector",
)

# If language changed, update and rerun immediately
if language != prev_lang:
    st.session_state.language = language
    st.rerun()

# Reload translation mapping for selected language
t = fl_config.translations[st.session_state.language]
st.markdown("---")

# Continue main content
st.title(t["title"])
st.caption(t["subtitle"])
st.markdown("---")


# --- PROGRESS TRACKER (now on top of Curriculum) ---
st.subheader(t["progress_tracker"])
total_topics = 45  # total placeholder
progress = len(st.session_state.completed_topics)
st.progress(progress / total_topics)
st.write(f"**{t['progress']}:** {progress}/{total_topics}")
st.markdown("---")

# --- CURRICULUM SECTION ---
st.subheader(t["curriculum"])

print(f'Language state : {st.session_state.language}')

topics = fl_config.topics_language[st.session_state.language]

for section, subtopics in topics.items():
    with st.expander(f"📂 {section}", expanded=False):
        for i, topic in enumerate(subtopics):
            completed = topic in st.session_state.completed_topics
            locked = not completed and any(
                t not in st.session_state.completed_topics for t in subtopics[:i]
            )
            if locked:
                st.button(f"🔒 {topic}", disabled=True)
            elif completed:
                st.success(f"✅ {topic} (Completed)")
            else:
                if st.button(f"▶️ {topic}"):
                    st.session_state.selected_topic = topic

# # --- TOPIC PROMPT ---
# if "selected_topic" in st.session_state:
#     st.markdown("---")
#     st.subheader(f"📖 {st.session_state.selected_topic}")
#     st.info(t["prompt"])
#     st.text_area("Your Answer / Prompt Input", key="user_input")
#     st.button(t["submit_test"], key="submit_test")

# --- FOOTER ---
st.markdown("---")
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('<div class="floating-btn">', unsafe_allow_html=True)
    if st.button("⬅️ Back", key="float_back"):
        st.session_state['page_status'] = 'welcome'
        del st.session_state.selected_option
        st.switch_page("pages/welcome.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.button(t["logout"]):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("You have been logged out.")
        # st.stop()
        finance_app_main.run()

    # Create container for the button
    # Create container for the button