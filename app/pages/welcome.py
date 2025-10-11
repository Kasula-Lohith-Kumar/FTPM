import streamlit as st
import registration as r
import pandas as pdd
from .. import authentication

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

def run():
    # --- How to display this on your Home Page ---
    # You can use tabs or expanders to separate Registration and Login

    # In your main Streamlit file (e.g., streamlit_app.py):

    st.header("Welcome to the Finance App")
    st.write("Please register or log in to access your portfolio dashboard.")

    # Create two tabs: Login and Register
    tab1, tab2 = st.tabs(["🔒 Login", "✍️ Register"])

    # with tab2:
    #     r.registration_form()

    with tab2:
    # Call the registration form and check its return value
        registration_status = r.registration_form()
    
        if registration_status:
            # If registration was successful, hide the form 
            # and display a message pointing to the Login tab (tab1).
        
            # The form is hidden because registration_form() returns True and 
            # the st.success() message is displayed within the function call.
        
            # You can add a clear instruction here:
            st.markdown("---")
            st.info("✅ **Ready to go!** Please click on the **Login** tab to continue.")

    with tab1:
        st.subheader("Login")
        # Add your login form fields here (Username, Password)
        # The login logic would involve reading the Google Sheet to check the credentials.
        username_login = st.text_input("Username")
        password_login = st.text_input("Password", type="password")

        if authentication.login_verification(username_login, password_login):
            print("✅ Login successful!")
            print(f'Welcome to Finance App {username_login}!')
        else:
            print("❌ Login failed: Incorrect password.")
        
        if st.button("Login"):
            st.info("Login logic goes here (check credentials against your Google Sheet data).")
    
    st.markdown("""
        <style>
            .floating-btn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                z-index: 9999;
            }
        </style>
    """, unsafe_allow_html=True)

    # Create container for the button
    button_container = st.container()
    with button_container:
        st.markdown('<div class="floating-btn">', unsafe_allow_html=True)
        if st.button("⬅️ Back to Main Page", key="float_back"):
            st.switch_page("finance_app_main.py")
        st.markdown('</div>', unsafe_allow_html=True)


run()