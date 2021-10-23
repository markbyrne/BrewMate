from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'YOURSPREADSHEET_ID'
VALUE_INPUT_OPTION = 'USER_ENTERED'

def main():
    pass

def save_temp(brew_id, time, temp_f, heater_status):
    """Saves timestamp and temperature in F.
    """
    RANGE_NAME = brew_id+'!A1:C20000'

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    values = [
        [time, temp_f, heater_status],
        # Additional rows ...
    ]
    body = {
        'values': values
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption=VALUE_INPUT_OPTION, body=body).execute()
    print('{0} cells appended.'.format(result \
                                           .get('updates') \
                                           .get('updatedCells')))

if __name__ == '__main__':
    main()
