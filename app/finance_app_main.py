import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from pages import home
import registration as r
import json
from google_sheets import gsheets_config as gsc

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
            padding-top: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

def is_streamlit_cloud() -> bool:
    """Detect if running inside Streamlit Cloud deployment."""
    return "STREAMLIT_RUNTIME" in os.environ


if __name__ == "__main__":

    if is_streamlit_cloud():
        print('STREAMLIT_RUNTIME')
        json.loads(st.secrets["gcp_service_account"])
    else:
        print('LOCAL_RUNTIME')
        with open(r'app\google_sheets\financetutorapp-562157097710.json', 'r') as file:
            gsc.KEY_FILE_DATA= json.load(file)

    if 'page_status' not in st.session_state:
        st.session_state['page_status'] = 'home'

    # show_home_content()
    if st.session_state['page_status'] == 'home':
        home.show_home_content()

    if st.button("Launch Your Portfolio Dashboard 🚀", use_container_width=True):
        st.switch_page("pages/welcome.py")

    # if st.session_state['page_status'] == 'welcome':
    #     welcome.run()

    elif st.session_state['page_status'] == 'auth':
        authentiation.show_auth_options()

    elif st.session_state['page_status'] == 'dashboard':
        st.title("Welcome to Your Portfolio Dashboard! 📈")
        # This is where your main app functionality would live
        if st.button("Logout"):
            st.session_state['page_status'] = 'home'
            # st.experimental_rerun()