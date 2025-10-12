import streamlit as st

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
            padding-left: 3rem;
            padding-right: 2rem;
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

def run():
    # Set a default username for testing if not set
    if 'username' not in st.session_state:
        st.session_state.username = 'Lohith'

    st.markdown(
        f"""
        <h2 style='text-align:center;'>👋 Welcome, <span style="color:#4CAF50;">{st.session_state.username.capitalize()}</span>! <a href="#" style="text-decoration:none; color:inherit; font-size: 0.7em;">🔗</a></h2>
        <p style='text-align:center; font-size:18px;'>Select one of the features below to get started.</p>
        """,
        unsafe_allow_html=True
    )

    # Custom CSS for the feature cards (not the button itself now)
    st.markdown("""
    <style>
    .feature-card {
        background-color: #111827;
        color: white;
        border-radius: 15px;
        padding: 25px;
        margin: 10px;
        text-align: center;
        box-shadow: 0px 2px 8px rgba(255,255,255,0.05);
        transition: all 0.3s ease;
        height: 265px;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 4px 16px rgba(255,255,255,0.6);
    }
    .feature-icon {
        font-size: 40px;
    }
    .feature-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 10px;
    }
    .feature-desc {
        font-size: 16px;
        margin-top: 8px;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

    # Layout for 3 features
    col1, col2, col3 = st.columns(3)

    # Use simple button labels and rely on markdown for the card appearance
    with col1:
        # Use simple label for button
        if st.button("📈 Data-Driven Insights", key="insights"):
            st.session_state.selected_option = "Data Insights"
        # Use markdown for the descriptive card
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon"></div>
                <div class="feature-title">Data-Driven Insights</div>
                <div class="feature-desc">Analyze asset performance and track your holdings with real-time data visualizations.</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🧠 Financial Literacy", key="literacy"):
            st.session_state.selected_option = "Financial Literacy"
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon"></div>
                <div class="feature-title">Financial Literacy</div>
                <div class="feature-desc">Access interactive tutorials and definitions to build a strong foundation in finance.</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        if st.button("🔒 Smart Portfolio Tracking", key="tracking"):
            st.session_state.selected_option = "Portfolio Tracking"
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon"></div>
                <div class="feature-title">Smart Portfolio Tracking</div>
                <div class="feature-desc">Securely log transactions and see how market changes affect your overall wealth.</div>
            </div>
        """, unsafe_allow_html=True)

    # --------------- NEXT STEPS SECTION ---------------
    if "selected_option" in st.session_state:
        st.markdown("---")
        st.markdown(f'<p style="font-size: 22px; font-weight: 700; margin-bottom: 5px;">🚀 You selected: <span style="font-weight: 800;">{st.session_state.selected_option}</span></p>', unsafe_allow_html=True)

        # Removed st.info and replaced with custom markdown for consistent styling
        if st.session_state.selected_option == "Data Insights":
            st.markdown('<div style="background-color: #262730; padding: 10px 15px; border-radius: 8px; border-left: 5px solid #007bff;"><span style="color: #6c757d;">📊 Launching Data Visualization Module...</span></div>', unsafe_allow_html=True)
        elif st.session_state.selected_option == "Financial Literacy":
            st.markdown('<div style="background-color: #262730; padding: 10px 15px; border-radius: 8px; border-left: 5px solid #007bff;"><span style="color: #6c757d;">🧭 Opening Financial Learning Resources...</span></div>', unsafe_allow_html=True)
        elif st.session_state.selected_option == "Portfolio Tracking":
            st.markdown('<div style="background-color: #262730; padding: 10px 15px; border-radius: 8px; border-left: 5px solid #007bff;"><span style="color: #6c757d;">💼 Loading Portfolio Tracker...</span></div>', unsafe_allow_html=True)

    button_container = st.container()
    with button_container:
        st.markdown('<div class="floating-btn">', unsafe_allow_html=True)
        if st.button("🚪🏃 Log Out", key="float_back"):
            if 'selected_option' in st.session_state:
                del st.session_state.selected_option
            st.session_state['page_status'] = 'home'
            st.switch_page("finance_app_main.py")
        st.markdown('</div>', unsafe_allow_html=True)


# ... (rest of the initialization code remains the same)
if 'page_status' not in st.session_state:
    st.session_state['page_status'] = 'login' # Start at login/home page
    st.switch_page("pages/login.py")

if 'username' not in st.session_state:
    # A username doesn't exist yet, so we don't set a default display name.
    # We just ensure the key exists, but it's okay to leave it blank or None for now.
    st.session_state['username'] = None 

if st.session_state['page_status'] == 'welcome':
    run()