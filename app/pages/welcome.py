import streamlit as st

def run():
    # 🔹 CSS Reset and Styling
    st.markdown("""
        <style>
        html, body, [class*="block-container"] {
            all: unset;
            font-family: "Source Sans Pro", sans-serif;
            font-size: 16px !important;
            line-height: 1.4;
            color: white;
        }

        .block-container {
            padding: 0 !important;
            margin: 0 auto !important;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 90vh; /* Center vertically */
            flex-direction: column;
        }

        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        p {
            font-size: 16px;
            margin-bottom: 0.5rem;
        }

        /* Hide sidebar and Streamlit elements */
        [data-testid="stSidebarNav"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }
        #MainMenu, footer, header {
            visibility: hidden;
        }

        /* Button styling */
        div.stButton > button {
            background-color: #1f2937;
            color: white;
            border: 1px solid #374151;
            border-radius: 10px;
            padding: 12px 18px;
            font-size: 17px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
        }

        div.stButton > button:hover {
            background-color: #2563eb;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.4);
        }

        [key="float_back"] button {
            background-color: #b91c1c !important;
            color: white !important;
            font-size: 16px !important;
            padding: 10px 20px !important;
            width: auto !important;
        }

        .feature-container {
            width: 85%;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            text-align: center;
            gap: 50px;
            margin-top: 40px;
        }

        .feature-box {
            max-width: 300px;
        }

        .feature-title {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .feature-desc {
            font-size: 15px;
            line-height: 1.5;
            color: #d1d5db;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Default username ---
    if 'username' not in st.session_state:
        st.session_state.username = 'Lohith'

    st.markdown(
        f"""
        <div style="text-align:center;">
            <h2>👋 Welcome, <span style="color:#4CAF50;">{st.session_state.username.capitalize()}</span>!</h2>
            <p style='font-size:18px;'>Select one of the features below to get started.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Centered Feature Section ---
    st.markdown('<div class="feature-container">', unsafe_allow_html=True)

    # Feature 1
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-box"><div class="feature-title">📈 Data-Driven Insights</div><div class="feature-desc">Analyze asset performance and track your holdings with real-time data visualizations.</div></div>', unsafe_allow_html=True)
        if st.button("Data Insights", key="insights"):
            st.session_state.selected_option = "Data Insights"

    with col2:
        st.markdown('<div class="feature-box"><div class="feature-title">🧠 Financial Literacy</div><div class="feature-desc">Access interactive tutorials and definitions to build a strong foundation in finance.</div></div>', unsafe_allow_html=True)
        if st.button("Financial Literacy", key="literacy"):
            st.session_state.selected_option = "Financial Literacy"

    with col3:
        st.markdown('<div class="feature-box"><div class="feature-title">📊 Annual Report Analyzer</div><div class="feature-desc">Upload and analyze company financial reports to uncover trends, key metrics, and performance insights.</div></div>', unsafe_allow_html=True)
        if st.button("Report Analyzer", key="tracking"):
            st.session_state.selected_option = "Report Analyzer"

    st.markdown('</div>', unsafe_allow_html=True)

    # --- NEXT STEPS SECTION ---
    if "selected_option" in st.session_state:
        st.markdown("---")
        st.markdown(
            f"""<p style="font-size: 22px; font-weight: 700; margin-bottom: 5px;">
            🚀 You selected: <span style="font-weight: 800;">{st.session_state.selected_option}</span></p>""",
            unsafe_allow_html=True
        )

        if st.session_state.selected_option == "Data Insights":
            st.markdown('<div style="background-color: #262730; padding: 10px 15px; border-radius: 8px; border-left: 5px solid #007bff;"><span style="color: #6c757d;">📊 Launching Data Visualization Module...</span></div>', unsafe_allow_html=True)

        elif st.session_state.selected_option == "Financial Literacy":
            st.markdown('<div style="background-color: #262730; padding: 10px 15px; border-radius: 8px; border-left: 5px solid #007bff;"><span style="color: #6c757d;">🧭 Opening Financial Learning Resources...</span></div>', unsafe_allow_html=True)
            st.session_state['focus_area'] = 'literacy'
            st.session_state['page_status'] = 'financial_literacy'
            st.switch_page("pages/financial_literacy.py")

        elif st.session_state.selected_option == "Report Analyzer":
            st.markdown('<div style="background-color: #262730; padding: 10px 15px; border-radius: 8px; border-left: 5px solid #007bff;"><span style="color: #6c757d;">💼 Loading Portfolio Tracker...</span></div>', unsafe_allow_html=True)
            st.session_state['page_status'] = 'report_analyzer'
            st.switch_page("pages/report_analyzer.py")

    # --- LOGOUT BUTTON ---
    st.markdown('<div style="margin-top: 40px; text-align:center;">', unsafe_allow_html=True)
    if st.button("🏃 Logout", key="float_back"):
        if 'selected_option' in st.session_state:
            del st.session_state.selected_option
        st.session_state['page_status'] = 'home'
        st.switch_page("finance_app_main.py")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- INITIALIZATION LOGIC (unchanged) ---
    if 'page_status' not in st.session_state:
        st.session_state['page_status'] = 'login'
        st.switch_page("pages/login.py")

    if 'username' not in st.session_state:
        st.session_state['username'] = None

    if st.session_state['page_status'] == 'welcome':
        print(f"page state : {st.session_state['page_status']}")

run()
