import pandas as pd
# from gsheets_main import *
import gspread
from gsheets import gsheets_config as gsc
from google.oauth2.service_account import Credentials
from gspread import Client, Spreadsheet



def get_worksheet(key_file_path, spreadsheet_id, created_tab):
    gc = authenticate(key_file_path)
    spreadsheet = gc.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(created_tab)
    return worksheet


def connect_to_worksheet(
        spreadsheet_id: str,
        key_file_path: str = 'service_account_key.json'):
    try:
        created_tab = create_new_worksheet_tab(
            spreadsheet_id=gsc.SPREADSHEET_ID,
            new_worksheet_name=gsc.USERS_TAB_NAME,
            key_file_path=gsc.KEY_FILE_LOCATION
        )
        print(f'Created Tab : {created_tab}', type(created_tab))

        worksheet = get_worksheet(key_file_path, spreadsheet_id, created_tab)
        # gc = authenticate(key_file_path)
        # spreadsheet = gc.open_by_key(spreadsheet_id)
        # worksheet = spreadsheet.worksheet(created_tab)
        # print(f"Successfully connected to worksheet '{created_tab}'")

        return worksheet
    except Exception as e:
        print(f"Error connecting to sheet: {e}")
        # Handle connection error, e.g., check your ID and sharing permissions.

def authenticate(key_file_path: str = 'service_account_key.json'):
    # 1. Authenticate the Service Account
    credentials = Credentials.from_service_account_file(key_file_path, scopes=gsc.SCOPES)
    gc: Client = gspread.authorize(credentials)
    return gc

def create_new_worksheet_tab(
        spreadsheet_id: str,
        new_worksheet_name: str,
        rows: int = 100,
        cols: int = 20,
        key_file_path: str = 'service_account_key.json'
) -> str:
    """
    Creates a new worksheet (tab) inside an existing Google Spreadsheet file.

    Args:
        spreadsheet_id: The ID of the existing Google Sheet file.
        new_worksheet_name: The name for the new tab (e.g., "Monthly Log").
        rows: Initial number of rows for the new sheet.
        cols: Initial number of columns for the new sheet.
        key_file_path: Path to the Service Account JSON key file.

    Returns:
        The title of the new worksheet if successful.
    """

    # Define the required scopes

    try:

        gc = authenticate(key_file_path)
        if gc:
            print('Authentication Successful : Creating New Sheet...')

        if worksheet_exists(gc, spreadsheet_id, new_worksheet_name, key_file_path):
            print(f'File Already exists : {new_worksheet_name}:{type(new_worksheet_name)}')
            return new_worksheet_name

        # 2. Open the existing spreadsheet
        spreadsheet:Spreadsheet = gc.open_by_key(spreadsheet_id)
        print(f"Opened spreadsheet: '{spreadsheet.title}'")

        # 3. Create the new worksheet
        worksheet = spreadsheet.add_worksheet(
            title=new_worksheet_name,
            rows=rows,
            cols=cols
        )
        print(f'New tab Created :{worksheet}, {type(worksheet)}')

        return worksheet.title

    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def create_sheet():
    # Select the specific worksheet (e.g., the first tab)
    worksheet = Spreadsheet.sheet1

    return worksheet
    # OR open by name: worksheet = spreadsheet.worksheet("Sheet Name")

def write(worksheet, cell, content):
    worksheet.update(cell, [[content]])
    print(f"Updated cell : {cell}.")

def clear(worksheet, cell):
    worksheet.update(cell, [['']])
    print(f"Cleared cell : {cell}.")

def clear_(worksheet, cell):
    print(worksheet.clear(cell))


import gspread
from google.oauth2.service_account import Credentials
from gspread.client import Client
from gspread import Spreadsheet


def worksheet_exists(
        client: object,
        spreadsheet_id: str,
        worksheet_name: str,
        key_file_path: str = 'service_account_key.json') -> bool:
    """
    Checks if a worksheet with a given name exists in the target spreadsheet.

    Args:
        spreadsheet_id: The ID of the existing Google Sheet file.
        worksheet_name: The name of the tab to check for (case-sensitive).
        key_file_path: Path to the Service Account JSON key file.

    Returns:
        True if the worksheet exists, False otherwise.
    """

    try:
        # 2. Open the existing spreadsheet
        spreadsheet: Spreadsheet = client.open_by_key(spreadsheet_id)

        # 3. Get all worksheet objects in the spreadsheet
        all_worksheets = spreadsheet.worksheets()

        # 4. Iterate through the list and check the title of each worksheet
        print('Checking if the worksheet already present or not')
        for ws in all_worksheets:
            if ws.title == worksheet_name:
                print(f"--> Worksheet '{worksheet_name}' found. <--")
                return True

        print(f"Worksheet '{worksheet_name}' not found.")
        return False

    except Exception as e:
        # This catches errors like invalid file path, network issues, or
        # the Service Account not having access (e.g., if the sheet wasn't shared).
        print(f"An error occurred during sheet access: {e}")
        return False

def open_gsheet(spreadsheet_id: str,
        key_file_path: str = 'service_account_key.json'):
    credentials = Credentials.from_service_account_file(key_file_path, scopes=gsc.SCOPES)
    gc: Client = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(spreadsheet_id)

    return spreadsheet
