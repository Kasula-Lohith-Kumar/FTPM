import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Assuming you have a file with your gspread setup or a direct connection
# from your streamlit-gsheets-connection setup.
# We'll use the service account file directly for simplicity.

# # --- Configuration (Update these) ---
# REGISTRATION_SHEET_ID = 'YOUR_REGISTRATION_SHEET_ID'
# WORKSHEET_NAME = 'User_Data'  # Name of the tab for registrations
# KEY_FILE_LOCATION = 'service_account_key.json'
#
#
# # -----------------------------------

# def get_worksheet():
#     """Initializes and returns the gspread worksheet object."""
#     try:
#         SCOPES = [
#             'https://www.googleapis.com/auth/spreadsheets',
#             'https://www.googleapis.com/auth/drive'
#         ]
#         credentials = Credentials.from_service_account_file(
#             KEY_FILE_LOCATION,
#             scopes=SCOPES
#         )
#         gc = gspread.authorize(credentials)
#         spreadsheet = gc.open_by_key(REGISTRATION_SHEET_ID)
#         return spreadsheet.worksheet(WORKSHEET_NAME)
#     except Exception as e:
#         st.error(f"Database connection error: {e}. Check your Sheet ID and sharing permissions.")
#         return None


# def save_user_data(data_list):
#     """Appends a new row of data to the Google Sheet."""
#     worksheet = get_worksheet()
#     if worksheet:
#         try:
#             worksheet.append_row(data_list)
#             return True
#         except Exception as e:
#             st.error(f"Error saving data to sheet: {e}")
#             return False
#     return False


# --- Streamlit App Form ---

def registration_form():
    """Displays the registration form."""
    st.subheader("New User Registration")

    with st.form("registration_form"):
        full_name = st.text_input("Full Name *", max_chars=50)
        email = st.text_input("Email Address *", help="Used for important updates.")

        st.markdown("---")

        username = st.text_input("Username (Login ID) *", max_chars=30)
        # Use type="password" to hide the input
        return
        password = st.text_input("Password *", type="password", min_chars=6)
        confirm_password = st.text_input("Confirm Password *", type="password", min_chars=6)

        st.checkbox("I agree to the Terms and Conditions.", value=False)

        submitted = st.form_submit_button("Register Account")

        if submitted:
            # 1. Validation Checks
            if not all([full_name, email, username, password, confirm_password]):
                st.warning("Please fill in all required fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            # Basic email format check
            elif "@" not in email or "." not in email:
                st.error("Please enter a valid email address.")
            else:
                # 2. Prepare Data for Saving
                # Ensure the order matches your Google Sheet columns!
                user_data = [full_name, email, username, password]

                # 3. Save to Google Sheet
                with st.spinner("Creating your account..."):
                    if save_user_data(user_data):
                        st.success(f"Registration successful! Welcome, {full_name}. You can now proceed to login.")
                    else:
                        # Error will be displayed by the save_user_data function
                        pass


# --- How to display this on your Home Page ---
# You can use tabs or expanders to separate Registration and Login

# In your main Streamlit file (e.g., streamlit_app.py):

st.header("Welcome to the Finance App")
st.write("Please register or log in to access your portfolio dashboard.")

# Create two tabs: Login and Register
tab1, tab2 = st.tabs(["🔒 Login", "✍️ Register"])

with tab2:
    registration_form()

with tab1:
    st.subheader("Login")
    # Add your login form fields here (Username, Password)
    # The login logic would involve reading the Google Sheet to check the credentials.
    username_login = st.text_input("Username")
    password_login = st.text_input("Password", type="password")
    if st.button("Login"):
        st.info("Login logic goes here (check credentials against your Google Sheet data).")