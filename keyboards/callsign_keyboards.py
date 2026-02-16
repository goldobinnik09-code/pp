import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Function to initialize Google Sheets API

def init_google_sheets(creds_json):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scope)
    client = gspread.authorize(creds)
    return client

# Function to generate callsign selection keyboards

def generate_callsign_keyboard(spreadsheet_name, sheet_name):
    client = init_google_sheets('path_to_creds.json')  # Change to your creds file path
    sheet = client.open(spreadsheet_name).worksheet(sheet_name)
    callsigns = sheet.col_values(1)[1:]  # Assuming callsigns are in the first column, starting from the second row

    keyboard = []
    for callsign in callsigns:
        keyboard.append({'text': callsign, 'callback_data': callsign})

    return {'inline_keyboard': [keyboard]}
