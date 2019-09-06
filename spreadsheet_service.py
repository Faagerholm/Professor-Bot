import gspread
from oauth2client.service_account import ServiceAccountCredentials


class SpreadsheetService:

    def __init__(self):
        # use creds to create a client to interact with the Google Drive API
        scopes = ['https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scopes)
        self.client = gspread.authorize(creds)

    def insertRow(self, sheet_name="Studiehandboken_data", data=None):
        sheet = self.client.open(sheet_name).sheet1
        if data:
            sheet.append_row(data)

    def test(self):
        # Find a workbook by name and open the first sheet
        sheet = self.client.open("Studiehandboken_data").sheet1
        # Extract and print all of the values
        list_of_hashes = sheet.get_all_records()
        # print(list_of_hashes)


service = SpreadsheetService()
service.insertRow()
service.test()
