import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st


    
def  run():

    if 'page_status' not in st.session_state:
        print('In Main File 📌')
        st.session_state['page_status'] = 'home'

    if st.session_state['page_status'] == 'home':
        print('Switching ➡️  🏠️ Page')
        print(f"Session state : {st.session_state['page_status']}\n")
        st.switch_page("pages/home.py")


if __name__ == "__main__":

    run()