#----------------------------------запись CSV в мою таблицу----------------------------------------------------

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name('./NAME_OF_KEY.json', scope)
client = gspread.authorize(credentials)


spreadsheetId = client.open('Test_data').id                 # set spreadsheet ID.
sheetName = 'manager'                                                      # set sheet name you want to put the CSV data.
csvFile = './manager.csv'  # set the filename and path of csv file.

sh = client.open_by_key(spreadsheetId)
sh.values_update(
    sheetName,
    params={'valueInputOption': 'USER_ENTERED'},
    body={'values': list(csv.reader(open(csvFile)))}
)



sheetName = 'club'                                                      # set sheet name you want to put the CSV data.
csvFile = './club.csv'  # set the filename and path of csv file.

sh = client.open_by_key(spreadsheetId)
sh.values_update(
    sheetName,
    params={'valueInputOption': 'USER_ENTERED'},
    body={'values': list(csv.reader(open(csvFile)))}
)


             # set spreadsheet ID.
sheetName = 'source'                                                      # set sheet name you want to put the CSV data.
csvFile = './source.csv'  # set the filename and path of csv file.

sh = client.open_by_key(spreadsheetId)
sh.values_update(
    sheetName,
    params={'valueInputOption': 'USER_ENTERED'},
    body={'values': list(csv.reader(open(csvFile)))}
)


