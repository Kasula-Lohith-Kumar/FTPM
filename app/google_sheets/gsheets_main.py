import gspread
import google_sheets.gsheets_config as gsc
import google_sheets.gsheets_operations as gso
from google.oauth2.service_account import Credentials
import pandas as pd




if __name__ == '__main__':
    # Run the function

    worksheet = gso.connect_to_worksheet(gsc.SPREADSHEET_ID,  gsc.KEY_FILE_LOCATION)

    if worksheet:
    #
        print(type(worksheet))
        gso.write(worksheet, 'B1', 'User Name')
        gso.clear(worksheet, 'B1')



