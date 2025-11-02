import streamlit as st

def show_home_content():
    # Hide sidebar and set custom CSS
    st.markdown("""
    <style>
        /* Hide Streamlit's default elements for the home page */
        [data-testid="stSidebarNav"],
        section[data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        .block-container {
            padding: 3rem 5rem;
            font-family: 'Segoe UI', sans-serif;
        }

        h1, h2, h3 {
            font-weight: 600;
            color: #E6E6E6;
        }

        .main-title {
            text-align: center;
            font-size: 2.5rem;
            color: #FFFFFF;
            margin-bottom: 0.4rem;
        }

        .subtitle {
            text-align: center;
            font-size: 1.1rem;
            color: #B0B0B0;
            margin-bottom: 2rem;
        }

        /* ---------- FEATURE ROW (flex) ---------- */
        .feature-row {
            display: flex !important;
            flex-direction: row !important;
            gap: 1rem !important;
            align-items: stretch !important; /* core: stretch columns to same height */
            width: 100%;
        }

        /* Target Streamlit's nested column wrappers aggressively and force them to stretch */
        .feature-row > div,
        .feature-row > div > div,
        .feature-row > div > div > div,
        .feature-row > div > div > div > div {
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 0% !important;
            padding: 0 !important; /* remove added padding interfering with height */
            margin: 0 !important;
        }

        /* Feature Box styling - box itself stretches and is a column flex container */
        .feature-box {
            background-color: #0E1117;
            border: 1px solid #262730;
            border-radius: 14px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start;
            align-items: stretch;
            height: 100% !important;      /* ensure it fills the column */
            min-height: 312px;            /* defensive fallback to ensure visual parity */
        }

        .feature-box > * {
            /* avoid inner markdown margins causing visual height differences */
            margin: 0;
            padding: 0;
        }

        .feature-box:hover {
            border-color: #4169E1;
            transform: translateY(-3px);
        }

        .feature-icon {
            font-size: 1.8rem;
            margin-bottom: 0.6rem;
        }

        .feature-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #FFFFFF;
            margin-bottom: 0.5rem;
        }

        .feature-desc {
            font-size: 0.95rem;
            color: #B0B0B0;
            margin-top: auto; /* ensures description sits nicely towards the bottom if content is short */
            line-height: 1.5;
        }

        /* Button styling (unchanged, kept strong) */
        .stButton > button {
            background-color: #4169E1 !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            font-size: 1.05rem !important;
            padding: 0.75rem 2.5rem !important;
            border: none !important;
            width: 100% !important;
            max-width: 600px !important;
            box-shadow: 0 4px 10px rgba(65, 105, 225, 0.4) !important;
            transition: all 0.3s ease-in-out !important;
        }

        .stButton > button:hover {
            background-color: #3650B3 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 14px rgba(65, 105, 225, 0.5) !important;
        }

        /* Small responsive tweak so columns stack nicely on small screens */
        @media (max-width: 900px) {
            .feature-row { flex-direction: column !important; }
            .feature-box { min-height: 220px; }
        }
    </style>
""", unsafe_allow_html=True)


    # ---- Title ----
    st.markdown('<h1 class="main-title">Lohith\'s Finance App</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">The Smart Way to <b>Manage Your Portfolio</b> and <b>Master Finance</b> 💰📈</p>', unsafe_allow_html=True)

    # ---- Image and Intro ----
    col1, col2 = st.columns([1, 2], vertical_alignment="center")
    with col1:
        st.image("app/pages/image_ai.png", use_container_width=True) 
    with col2:
        st.info("Your comprehensive platform for **gaining financial knowledge** and **managing your portfolio effectively**.")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ---- Feature Cards (Wrapped in custom div for Flexbox) ----
    
    # 1. Start of the custom feature row container
    st.markdown('<div class="feature-row">', unsafe_allow_html=True) 
    
    # 2. Define Streamlit columns inside the custom div
    c1, c2, c3 = st.columns(3)
    
    # 3. Insert content
    with c1:
        st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">📈</div>
                <div class="feature-title">Data-Driven Insights</div>
                <div class="feature-desc">Analyze asset performance and track your holdings with real-time data visualizations.</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">Financial Literacy</div>
                <div class="feature-desc">Access interactive tutorials and definitions to build a strong foundation in finance.</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Annual Report Analyzer</div>
                <div class="feature-desc">Upload and analyze company financial reports to uncover trends, key metrics, and performance insights.</div>
            </div>
        """, unsafe_allow_html=True)
        
    # 4. End of the custom feature row container
    st.markdown('</div>', unsafe_allow_html=True) 

    # ---- Launch Button Section ----
    st.markdown("<br><hr><br>", unsafe_allow_html=True) 

    st.markdown(
        """
        <h3 style='text-align:center; color:white; margin-bottom: 1rem;'>Ready to Start?</h3>
        """,
        unsafe_allow_html=True
    )

    # Center the button 
    st.markdown(
        """
        <div style='display: flex; justify-content: center;'>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Launch Button 
    if st.button("Launch Your Portfolio Dashboard 🚀", use_container_width=True):
        st.session_state['page_status'] = 'login'
        st.switch_page("pages/login.py")


# ✅ Render only if on home page
if st.session_state.get('page_status') == 'home':
    show_home_content()