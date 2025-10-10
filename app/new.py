import streamlit as st

# 1. Initialize the state variable on the first run
if 'page_status' not in st.session_state:
    st.session_state['page_status'] = 'home' # Can be 'home', 'auth', or 'dashboard'


# --- Define the function that shows the button ---
def show_home_content():
    st.title("Finance App")
    st.write("App which helps in gaining knowledge on finance and portfolio management!")
    st.markdown("---")
    st.header("Ready to Start?")

    # When this button is clicked, change the state to 'auth'
    if st.button("Launch Your Portfolio Dashboard 🚀", use_container_width=True):
        st.session_state['page_status'] = 'auth'
        # Rerun the app to show the new content
        # st.experimental_rerun()


# --- Define the function that shows the Login/Register tabs ---
def show_auth_options():
    st.subheader("Access Your Dashboard")

    # Add a back button for better user experience
    if st.button("← Back to Home"):
        st.session_state['page_status'] = 'home'
        # st.experimental_rerun()
        return  # Stop execution to prevent code below from running immediately

    st.markdown("---")

    # Use tabs for a clean presentation of the two options
    tab1, tab2 = st.tabs(["🔒 Login", "✍️ Register"])

    with tab1:
        st.write("Please enter your credentials.")
        # Your login form fields (Username, Password) go here
        username_login = st.text_input("Username", key="login_user")
        password_login = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            # Implement your logic to check the Google Sheet for credentials
            st.success("Login logic would proceed to dashboard...")
            # st.session_state['page_status'] = 'dashboard'

    with tab2:
        # Call the registration function you created previously
        # For simplicity here, we'll just put a message:
        st.write("Create a new account.")
        # Your registration form (Full Name, Email, Password, etc.) goes here
        st.info("Registration form fields and GSheets saving logic...")
        if st.button("Complete Registration"):
            # Implement your GSheets saving logic here
            st.success("Registration completed! Please log in.")
            # Set state back to login tab for convenience
            # st.session_state['active_tab'] = 'login'


# --- Main App Execution Flow ---

if st.session_state['page_status'] == 'home':
    show_home_content()

elif st.session_state['page_status'] == 'auth':
    show_auth_options()

elif st.session_state['page_status'] == 'dashboard':
    st.title("Welcome to Your Portfolio Dashboard! 📈")
    # This is where your main app functionality would live
    if st.button("Logout"):
        st.session_state['page_status'] = 'home'
        # st.experimental_rerun()