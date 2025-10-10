import gspread
import gsheets_config as gsc
import gsheets_operations as gso
from google.oauth2.service_account import Credentials
import pandas as pd
import gsheets_config as gsc


def get_new_tab_name():
    new_tab_name = gso.create_new_worksheet_tab(
        spreadsheet_id=gsc.SPREADSHEET_ID,
        new_worksheet_name=gsc.USERS_TAB_NAME,
        key_file_path=gsc.KEY_FILE_LOCATION
    )
    return new_tab_name

if __name__ == '__main__':
    # Run the function

    created_tab = get_new_tab_name()
    print(f'Created Tab : {created_tab}', type(created_tab))
    worksheet = gso.connect_to_worksheet(gsc.SPREADSHEET_ID, created_tab, gsc.KEY_FILE_LOCATION)

    if worksheet:
    #
        print(type(worksheet))
        gso.write(worksheet, 'B1', 'User Name')
        gso.clear(worksheet, 'B1')


