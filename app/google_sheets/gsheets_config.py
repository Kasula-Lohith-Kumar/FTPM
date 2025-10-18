SPREADSHEET_ID = '1TxGh-JuEWEmopvpHosUnDfstPGSYH_CzzOJCkCTWuaE'
LOCAL_KEY_PATH = r"app\google_sheets\financetutorapp-562157097710.json"
USERS_TAB_NAME = "UserData"
TOPICS_TAB = "Topics"
KEY_FILE_DATA = None
WORKSHEET = None
EMAIL_COL_INDEX = 2
USER_NAME_COL_INDEX = 3
USER_TOPICS_STATUS_COL_INDEX = 5
USER_TOPICS_STATUS_COL_NAME = 'Topics_Status'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets', # For Sheets API access
    'https://www.googleapis.com/auth/drive'        # For Drive API to open the sheet
]