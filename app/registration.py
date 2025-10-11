import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


def registration_form():
    """Displays the registration form."""

    registration_details = {'Status' : False}
    st.subheader("New User Registration")

    with st.form("registration_form"):
        full_name = st.text_input("Full Name *", max_chars=50)
        registration_details['Full_Name'] = full_name

        email = st.text_input("Email Address *", help="Used for important updates.")
        registration_details['Email'] = email

        st.markdown("---")

        username = st.text_input("Username (Login ID) *", max_chars=30)
        registration_details['User_Name'] = username
        # Use type="password" to hide the input
        
        # FIX: Removed the invalid 'min_chars' argument
        password = st.text_input("Password *", type="password")
        # FIX: Removed the invalid 'min_chars' argument
        confirm_password = st.text_input("Confirm Password *", type="password")

        # You would typically add the form submission button and validation logic here
        submitted = st.form_submit_button("Register")
        
        if submitted:
            # --- Custom Validation Logic ---
            if len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif not full_name or not email or not username or not password or not confirm_password:
                st.error("Please fill in all required fields (*).")
            else:
                registration_details['Password'] = confirm_password
                # Add your registration logic here (e.g., save to database)
                st.success(f"Registration successful for {username}!")
                registration_details['Status'] = True
            return registration_details['Status']
        
    return registration_details['Status']