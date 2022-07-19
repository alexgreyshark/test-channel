from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'sheet_google.json'

def google_sheet_connect():
    """Возвращает подключение к GOOGLE_SHEET при запуске сервера
    """
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    return sheet