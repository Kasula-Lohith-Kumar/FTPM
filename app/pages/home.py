import streamlit as st

def show_home_content():
    # Hide sidebar and set custom CSS
    st.markdown("""
    <style>
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

        .feature-row {
            display: flex !important;
            flex-direction: row !important;
            gap: 1rem !important;
            align-items: stretch !important;
            width: 100%;
        }

        .feature-row > div,
        .feature-row > div > div,
        .feature-row > div > div > div,
        .feature-row > div > div > div > div {
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 0% !important;
            padding: 0 !important;
            margin: 0 !important;
        }

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

        /* 🔥 new size control */
        width: 275px !important;
        min-height: 200px !important;
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
            line-height: 1.5;
        }

        @media (max-width: 900px) {
            .feature-row { flex-direction: column !important; }
            .feature-box { min-height: 220px; }
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">Lohith\'s Finance App</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">The Smart Way to <b>Manage Your Portfolio</b> and <b>Master Finance</b> 💰📈</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("app/pages/image_ai.png", use_container_width=True) 
    with col2:
        st.info("Your comprehensive platform for **gaining financial knowledge** and **managing your portfolio effectively**.")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Feature Cards (updated: only 2)
    st.markdown('<div class="feature-row">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">Financial Literacy</div>
                <div class="feature-desc">Access interactive tutorials and definitions to build a strong foundation in finance.</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
            <div class="feature-box">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Annual Report Analyzer</div>
                <div class="feature-desc">Upload and analyze company financial reports to uncover insights and performance metrics.</div>
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
    st.markdown("""
    <style>

    div.stButton > button {
        background-color: #00b894 !important; /* Change color */
        color: white !important;              /* Text color */
        border-radius: 12px !important;       /* Rounded corners */
        font-size: 18px !important;
        padding: 12px 24px !important;
        border: none !important;
        cursor: pointer;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background-color: #019267 !important; /* Hover effect */
    }

    </style>
    """, unsafe_allow_html=True)

    # Launch Button 
    if st.button("Launch Your Portfolio Dashboard 🚀", use_container_width=True):
        st.session_state['page_status'] = 'login'
        st.switch_page("pages/login.py")


if "page_status" not in st.session_state:
    st.session_state["page_status"] = "home"

if st.session_state["page_status"] == "home":
    show_home_content()