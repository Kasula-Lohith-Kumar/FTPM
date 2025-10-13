import streamlit as st
import gspread
from  app.google_sheets import gsheets_config as gsc
from  app.google_sheets import gsheets_operations as gso


def login_verification(input_username: str, input_password: str) -> bool:
    """
    Verifies user credentials against data in a Google Sheet.
    
    This function looks up the input_username and checks if the corresponding 
    password in the sheet matches the input_password.

    Args:
        input_username (str): The username entered by the user.
        input_password (str): The password entered by the user.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    try:
        worksheet = gso.get_worksheet(gsc.KEY_FILE_DATA, gsc.SPREADSHEET_ID, gsc.USERS_TAB_NAME)
        user_records = worksheet.get_all_records()
        
        # 3. SEARCH FOR USERNAME AND VERIFY PASSWORD
        for record in user_records:
            # gspread.get_all_records() uses the column headers as dictionary keys
            
            # Find a matching username
            if record.get('User_Name') == input_username:
                # Username found! Now check the password
                
                # NOTE: For real-world systems, passwords should be HASHED, 
                # not stored as plain text. This code uses plain text for simplicity.
                if record.get('Password') == input_password:
                    print("✅ Login successful! Welcome.")
                    return True
                else:
                    # Username is correct, but password is wrong
                    print("❌ Login failed: Incorrect password.")
                    return False

        # If the loop finishes without finding the username
        print("❌ Login failed: Incorrect user name or user not found.")
        return False

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return False
    
def check_for_duplicates(worksheet, new_email: str, new_username: str) -> dict:
    """
    Checks if a new email or username already exists in the worksheet.

    Args:
        worksheet: The gspread Worksheet object.
        new_email (str): The email address to check.
        new_username (str): The username to check.

    Returns:
        dict: A dictionary indicating which fields are duplicates.
              Example: {'is_email_duplicate': True, 'is_username_duplicate': False}
    """
    
    # Initialize the results
    result = {
        'is_email_duplicate': False,
        'is_username_duplicate': False
    }

    try:
        # 1. FETCH ALL EXISTING EMAILS (Column B)
        # We specify the column index (2) and fetch values starting from row 2 (to skip the header)
        # By setting value_render_option='UNFORMATTED_VALUE', we ensure we get the raw string.
        email_column_data = worksheet.col_values(gsc.EMAIL_COL_INDEX, value_render_option='UNFORMATTED_VALUE')
        # print(f'E-mail column data : {email_column_data}')
        
        # The list includes the header (Email), so we remove it
        existing_emails = {e.strip().lower() for e in email_column_data[1:] if e.strip()}
        
        # 2. FETCH ALL EXISTING USERNAMES (Column C)
        username_column_data = worksheet.col_values(gsc.USER_NAME_COL_INDEX, value_render_option='UNFORMATTED_VALUE')
        # print(f'User column data : {username_column_data}')         
        # The list includes the header (User_Name), so we remove it
        existing_usernames = {u.strip().lower() for u in username_column_data[1:] if u.strip()}

        # 3. PERFORM THE CHECKS (Case-insensitive)
        
        # Check for Email
        if new_email.lower() in existing_emails:
            result['is_email_duplicate'] = True
            
        # Check for Username
        if new_username.lower() in existing_usernames:
            result['is_username_duplicate'] = True

    except Exception as e:
        print(f"❌ Error during duplicate check: {e}")
        # Return default (False) to prevent registration due to error
        return {'is_email_duplicate': True, 'is_username_duplicate': True}

    return result

import re

def validate_email_format(email_address: str) -> bool:
    """
    Validates the format of an email address using a regular expression.
    
    The pattern checks for:
    1. One or more characters (letters, numbers, specific symbols) before the @.
    2. A single '@' symbol.
    3. One or more characters after the @ (the domain name).
    4. A period (dot).
    5. Two or more characters at the end (the TLD like .com, .org, .co.uk).

    Args:
        email_address (str): The email string to validate.

    Returns:
        bool: True if the format is valid, False otherwise.
    """
    
    # Simple, reliable regex pattern for general email validation
    # This pattern covers most common email formats.
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    # The re.fullmatch() function checks if the entire string matches the pattern
    if re.fullmatch(regex, email_address):
        return True
    else:
        return False
