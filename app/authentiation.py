import streamlit as st
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