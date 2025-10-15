import streamlit as st
from pages import fl_config
from app import finance_app_main

def run():
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

    # --- INITIAL SESSION STATE & LANGUAGE SETUP ---
    if "username" not in st.session_state:
        st.session_state.username = "Lohith"

    if "language" not in st.session_state:
        st.session_state.language = "English"

    # Current language and translations
    lang = st.session_state.language
    t = fl_config.translations[lang]

    # --- CANONICAL SECTIONS (language-agnostic keys) ---
    # Use English ordering as canonical internal section IDs.
    canonical_sections = list(fl_config.topics_language["English"].keys())

    # Build localized section list for the current language (order must match canonical)
    localized_section_list = list(fl_config.topics_language[lang].keys())

    # If languages have different number of sections, align lengths by padding/truncating
    # (This is defensive; ideally number of sections is same across languages.)
    if len(localized_section_list) < len(canonical_sections):
        # pad localized_section_list with English fallback titles
        localized_section_list += canonical_sections[len(localized_section_list):]
    elif len(localized_section_list) > len(canonical_sections):
        # truncate localized list to canonical length
        localized_section_list = localized_section_list[: len(canonical_sections)]

    # Map canonical_section_id -> localized section title for current language
    section_title_map = dict(zip(canonical_sections, localized_section_list))

    # --- TOPICS FOR CURRENT LANGUAGE (localized) ---
    # We'll build a dict: canonical_key -> list_of_localized_topics
    topics_localized_by_canonical = {}
    for idx, canon in enumerate(canonical_sections):
        # Get localized section title
        loc_title = section_title_map[canon]
        # Get localized topics list for this section; if missing, fallback to English
        localized_topics = fl_config.topics_language[lang].get(loc_title, fl_config.topics_language["English"][canon])
        topics_localized_by_canonical[canon] = localized_topics

    # --- INITIALIZE completed_topics (stored under canonical keys) ---
    # Each canonical section has a list of states ["No"/"Start"/"Yes"] length = number of topics in that localized section.
    if "completed_topics" not in st.session_state or not isinstance(st.session_state.completed_topics, dict):
        st.session_state.completed_topics = {
            canon: ["No" for _ in topics_localized_by_canonical[canon]] for canon in canonical_sections
        }

    # If language changed or topic counts changed, ensure lengths match current localized topic lists
    for canon in canonical_sections:
        desired_len = len(topics_localized_by_canonical[canon])
        curr = st.session_state.completed_topics.get(canon, [])
        if len(curr) < desired_len:
            # extend with "No"
            st.session_state.completed_topics[canon] = curr + ["No"] * (desired_len - len(curr))
        elif len(curr) > desired_len:
            # truncate to desired length
            st.session_state.completed_topics[canon] = curr[:desired_len]

    # --- MAIN HEADER (Welcome first, then language selection) ---
    # Welcome message
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

    if language != prev_lang:
        st.session_state.language = language
        # important: rerun so mapping and UI refresh immediately
        st.rerun()

    # Reload current language variables after potential change
    lang = st.session_state.language
    t = fl_config.translations[lang]

    # Rebuild localized mappings for the (possibly new) language
    localized_section_list = list(fl_config.topics_language[lang].keys())
    if len(localized_section_list) < len(canonical_sections):
        localized_section_list += canonical_sections[len(localized_section_list):]
    elif len(localized_section_list) > len(canonical_sections):
        localized_section_list = localized_section_list[: len(canonical_sections)]
    section_title_map = dict(zip(canonical_sections, localized_section_list))
    topics_localized_by_canonical = {
        canon: fl_config.topics_language[lang].get(section_title_map[canon], fl_config.topics_language["English"][canon])
        for canon in canonical_sections
    }

    # Ensure lengths still match after language switch
    for canon in canonical_sections:
        desired_len = len(topics_localized_by_canonical[canon])
        curr = st.session_state.completed_topics.get(canon, [])
        if len(curr) < desired_len:
            st.session_state.completed_topics[canon] = curr + ["No"] * (desired_len - len(curr))
        elif len(curr) > desired_len:
            st.session_state.completed_topics[canon] = curr[:desired_len]

    st.markdown("---")

    # --- MAIN CONTENT & PROGRESS ---
    st.title(t["title"])
    st.caption(t["subtitle"])
    st.markdown("---")

    st.subheader(t["progress_tracker"])
    total_topics = sum(len(v) for v in topics_localized_by_canonical.values())
    progress = sum(
        1
        for canon in canonical_sections
        for state in st.session_state.completed_topics[canon]
        if state == "Yes"
    )
    st.progress(progress / (total_topics or 1))
    st.write(f"**{t['progress']}:** {progress}/{total_topics}")
    st.markdown("---")

    # --- CURRICULUM SECTION ---
    st.subheader(t["curriculum"])

    # Determine which canonical section index is unlocked (first not fully Yes)
    section_unlock_index = 0
    for i, canon in enumerate(canonical_sections):
        if not all(s == "Yes" for s in st.session_state.completed_topics[canon]):
            section_unlock_index = i
            break
    else:
        section_unlock_index = len(canonical_sections) - 1

    # Display each canonical section, but show localized title & localized topics
    for s_index, canon in enumerate(canonical_sections):
        print(f'canonical_sections : {canonical_sections}')
        loc_section_title = section_title_map[canon]
        print(f'loc_section_title : {loc_section_title}')
        subtopics = topics_localized_by_canonical[canon]
        print(f'subtopics : {subtopics}')

        with st.expander(f"📂 {loc_section_title}", expanded=False):
            section_locked = s_index > section_unlock_index

            for i, topic_localized in enumerate(subtopics):
                topic_state = st.session_state.completed_topics[canon][i]

                # locked if this section is locked or previous topic not completed
                locked = section_locked or (i > 0 and st.session_state.completed_topics[canon][i - 1] != "Yes")

                if locked:
                    # ensure canonical state stored as "No"
                    st.session_state.completed_topics[canon][i] = "No"
                    st.button(f"🔒 {topic_localized}", disabled=True)
                elif topic_state == "Yes":
                    st.success(f"✅ {topic_localized} (Completed)")
                elif topic_state == "Start":
                    if st.button(f"▶️ {topic_localized}"):
                        st.session_state.selected_topic = (canon, i, topic_localized)   
                        print(f'st.session_state.selected_topic : {st.session_state.selected_topic}')
                        st.session_state['canon_topic_index'] = (s_index, i)
                        print(f"canon_topic_index : {st.session_state['canon_topic_index']}")
                        st.session_state['page_status'] = 'fl_topic'
                        st.switch_page("pages/fl_topic.py")
                else:  # default -> set to Start (available to start)
                    st.session_state.completed_topics[canon][i] = "Start"
                    if st.button(f"▶️ {topic_localized}"):
                        st.session_state.selected_topic = (canon, i, topic_localized)
                        st.session_state['canon_topic_index'] = (s_index, i)
                        print(f"canon_topic_index : {st.session_state['canon_topic_index']}")
                        st.session_state['page_status'] = 'fl_topic'
                        st.switch_page("pages/fl_topic.py")

    # # --- TOPIC PROMPT AREA ---
    # if "selected_topic" in st.session_state:
    #     canon, idx, topic_localized = st.session_state.selected_topic
    #     st.markdown("---")
    #     st.subheader(f"📖 {topic_localized}")
    #     st.info(t["prompt"])
    #     user_input = st.text_area("Your Answer / Prompt Input", key="user_input")

    #     if st.button(t["submit_test"]):
    #         # Mark the canonical slot as completed
    #         st.session_state.completed_topics[canon][idx] = "Yes"
    #         st.success("✅ Topic marked as completed!")
    #         # remove selection and rerun to refresh UI (unlock next topics/sections)
    #         del st.session_state["selected_topic"]
    #         st.rerun()


    # --- FOOTER ---
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<div class="floating-btn">', unsafe_allow_html=True)
        if st.button(f"⬅️ {t['back']}", key="float_back"):
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


# ... (rest of the initialization code remains the same)
if 'page_status' not in st.session_state:
    st.session_state['page_status'] = 'login' # Start at login/home page
    st.switch_page("pages/login.py")

if 'username' not in st.session_state:
    # A username doesn't exist yet, so we don't set a default display name.
    # We just ensure the key exists, but it's okay to leave it blank or None for now.
    st.session_state['username'] = None 

if st.session_state['page_status'] == 'financial_literacy':
    print(f"page state : {st.session_state['page_status']}")
    run()