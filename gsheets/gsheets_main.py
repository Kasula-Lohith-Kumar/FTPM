import gspread
import gsheets_config as gsc
import gsheets_operations as gso
from google.oauth2.service_account import Credentials
import pandas as pd
import gsheets_config as gsc




if __name__ == '__main__':
    # Run the function

    worksheet = gso.connect_to_worksheet(gsc.SPREADSHEET_ID,  gsc.KEY_FILE_LOCATION)

    if worksheet:
    #
        print(type(worksheet))
        gso.write(worksheet, 'B1', 'User Name')
        gso.clear(worksheet, 'B1')



