import streamlit as st
import gspread
from google_sheets import gsheets_operations as gso
from google_sheets import gsheets_config as gsc
import authentication

REG_COL_INDEX = 0
REG_COL_RANGE = 'A1:D1'
EXPECTED_HEADERS = ['Full_Name', 'Email', 'User_Name', 'Password']

def registration_form():
    """Displays the registration form."""

    registration_details = {'Status' : False}
    st.subheader("New User Registration")

    with st.form("registration_form"):
        full_name = st.text_input("Full Name *", max_chars=50)
        registration_details['Full_Name'] = full_name

        email = st.text_input("Email Address *", help="Used for important updates.")
        email_status = authentication.validate_email_format(email)
        registration_details['Email'] = email

        st.markdown("---")

        username = st.text_input("Username (Login ID) *", max_chars=30)
        registration_details['User_Name'] = username
        # Use type="password" to hide the input
        
        # FIX: Removed the invalid 'min_chars' argument
        password = st.text_input("Password *", type="password", help="Min 6 and Max 15 Characters Long")
        # FIX: Removed the invalid 'min_chars' argument
        confirm_password = st.text_input("Confirm Password *", type="password")

        # You would typically add the form submission button and validation logic here
        submitted = st.form_submit_button("Register")
        
        if submitted:
            # --- Custom Validation Logic ---
            if len(password) < 6 or len(password) > 15:
                st.error("Password must be 6 to 15 characters long.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif not full_name or not email or not username or not password or not confirm_password:
                st.error("Please fill in all required fields (*).")
            elif not email_status:
                st.error("Please provide the valid email id.")
            else:
                registration_details['Password'] = confirm_password
                sheet = gso.connect_to_worksheet(gsc.SPREADSHEET_ID,  gsc.KEY_FILE_DATA)         

                if sheet:
                    # Data to append (make sure the order matches your Sheet columns)
                    user_data = [
                        registration_details['Full_Name'],
                        registration_details['Email'],
                        registration_details['User_Name'],
                        registration_details['Password']
                        # You might want to store a timestamp here too
                    ]
                    result = authentication.check_for_duplicates(sheet, registration_details['Email'],
                                                                  registration_details['User_Name'])
                    try:
                        # Append the new row to the sheet, gspread automatically increments the row
                        if (result['is_email_duplicate'] == False) and (result['is_username_duplicate'] == False):
                            if not check_reg_cols(sheet):
                                write_headers_to_worksheet(sheet, REG_COL_RANGE)
                            
                            sheet.append_row(user_data)
                            st.success(f"✅ Registration successful for '{username}'! Data saved.")
                            registration_details['Status'] = True
                        else:
                            st.error(f"❌ Registration Filed for '{username}', user-name or e-mail already exists")
                    except Exception as e:
                        st.error(f"Failed to save data to Google Sheet. Error: {e}")
                        registration_details['Status'] = False # Ensure status is False on DB failure
                else:
                    st.error("Could not proceed with registration due to a connection error.")
                    registration_details['Status'] = False

        
    return registration_details['Status']


def check_reg_cols(worksheet) -> bool:
    """
    Checks if the header row (A1 to D1) of the worksheet matches the 
    required column names using a single API call.

    Args:
        worksheet: The gspread Worksheet object to check.

    Returns:
        bool: True if the headers match, False otherwise.
    """
    
    # 1. Define the expected header list
    EXPECTED_HEADERS = ['Full_Name', 'Email', 'User_Name', 'Password']
    
    # 2. Get the values of the header row (A1 to D1) in a single API call
    # .get_values() returns a list of lists (e.g., [['Full_Name', 'Email', ...]])
    # We only need the first element (the row itself)
    try:
        header_row = worksheet.get_values('A1:D1')
    except gspread.exceptions.APIError as e:
        print(f"Error fetching header row: {e}")
        return False
    
    # Check if data was returned and if the list is not empty
    if not header_row or not header_row[0]:
        return False
    
    # 3. Compare the fetched header row (header_row[0]) with the expected list
    return header_row[0] == EXPECTED_HEADERS
    
def write_headers_to_worksheet(
    worksheet, 
    start_cell: str = 'A1', 
    headers: list = EXPECTED_HEADERS
) -> dict:
    """
    Writes the header list to the specified starting cell of the worksheet 
    in a single, efficient API call.

    Args:
        worksheet: The gspread Worksheet object to update.
        start_cell: The A1 notation cell where the headers should begin (e.g., 'A1').
        headers: A list of strings representing the column headers.

    Returns:
        dict: The API response dictionary, or an empty dictionary on failure.
    """
    
    try:
        # Data must be a list of lists, so we wrap the headers list
        data_to_write = [headers]
        
        # Use the update() method with USER_ENTERED option 
        # (even though it's not strictly necessary for simple text headers, it's good practice)
        result = worksheet.update(
            start_cell, 
            data_to_write,
            value_input_option='USER_ENTERED'
        )
        
        # Log success and return the API result
        print(f"✅ Successfully wrote {len(headers)} headers starting at {start_cell}.")
        return result

    except gspread.exceptions.APIError as e:
        print(f"❌ API Error while writing headers: {e}")
        return {}
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return {}

    
