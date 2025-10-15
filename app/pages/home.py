import streamlit as st

def show_home_content():
    # st.sidebar.title('Navigation')
    # selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    #
    # page = PAGES[selection]
    # page.app()

    # Hides the default sidebar
    # st.markdown("""
    # <style>
    #     [data-testid="stSidebarNav"] {display: none;}
    #     section[data-testid="stSidebar"] {display: none;}
    #     [data-testid="collapsedControl"] {display: none;}
    # </style>
    # """, unsafe_allow_html=True)
    # --- Hide sidebar and adjust layout ---
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
            section[data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
            .block-container {
                padding-left: 6rem;
                padding-right: 2rem;
                padding-top: 1rem;
            }
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

    st.title("Finance App")
    st.markdown("## The Smart Way to **Manage Your Portfolio** and **Master Finance** 💰📈")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("app/pages/image_ai.png")  # Or use st.markdown("# 🧠")
    with col2:
        st.info(
            "Your comprehensive platform for **gaining knowledge on finance** and **effective portfolio management**.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 📈 Data-Driven Insights")
        st.write("Analyze asset performance and track your holdings with real-time data visualizations.")

    with c2:
        st.markdown("### 🧠 Financial Literacy")
        st.write("Access interactive tutorials and definitions to build a strong foundation in finance.")

    with c3:
        st.markdown("### 🔒 Smart Portfolio Tracking")
        st.write("Securely log transactions and see how market changes affect your overall wealth.")

    st.markdown("---")
    st.subheader("Ready to Start?")
    if st.button("Launch Your Portfolio Dashboard 🚀", use_container_width=True):
        st.session_state['page_status'] = 'login'
        st.switch_page("pages/login.py")
    # st.button("Launch Your Portfolio Dashboard 🚀", use_container_width=True)
    # The sidebar navigation should link to key pages here as well.


if st.session_state['page_status'] == 'home':
    show_home_content()