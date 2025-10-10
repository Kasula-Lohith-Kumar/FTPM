import streamlit as st
import home, authentiation
# import new
import registration as r

PAGES = {
    "Home": home,
    "Autentication" : authentiation
}



if __name__ == "__main__":

    if 'page_status' not in st.session_state:
        st.session_state['page_status'] = 'home'

    # show_home_content()
    if st.session_state['page_status'] == 'home':
        home.show_home_content()

    elif st.session_state['page_status'] == 'auth':
        authentiation.show_auth_options()

    elif st.session_state['page_status'] == 'dashboard':
        st.title("Welcome to Your Portfolio Dashboard! 📈")
        # This is where your main app functionality would live
        if st.button("Logout"):
            st.session_state['page_status'] = 'home'
            # st.experimental_rerun()