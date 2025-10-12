SPREADSHEET_ID = '1TxGh-JuEWEmopvpHosUnDfstPGSYH_CzzOJCkCTWuaE'
LOCAL_KEY_PATH = r"app\google_sheets\financetutorapp-562157097710.json"
USERS_TAB_NAME = "UserData"
KEY_FILE_DATA = None
WORKSHEET = None
EMAIL_COL_INDEX = 2
USER_NAME_COL_INDEX = 3

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets', # For Sheets API access
    'https://www.googleapis.com/auth/drive'        # For Drive API to open the sheet
]