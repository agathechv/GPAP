import os
import slack
import googleapiclient, httplib2, oauth2client
from googleapiclient import discovery
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
import io
from oauth2client import file, client, tools
import csv
from io import StringIO 
from csv import reader
import sqlite3
from flask import Flask, request
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# TODO: put me in my own function
creds = None
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
store = file.Storage('credentials.json')


if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            print(pickle)
            creds = pickle.load(token)

if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)    

drive_service = build('drive', 'v3', credentials=creds)

def download(file_id):

    request = drive_service.files().export_media(fileId=file_id, mimeType='text/csv')
    fileHandle = io.BytesIO()
    downloader = MediaIoBaseDownload(fileHandle, request)
    done = False
    while done is False:
        done = downloader.next_chunk()
        
    content=fileHandle.getvalue()
    str_content=content.decode()
    return str_content

def slackmsg(text_id):
  slack_token = os.environ["SLACK_API_TOKEN"] #export SLACK_API_TOKEN=xoxb-7...9r8
  client = slack.WebClient(token=slack_token)

  return client.chat_postMessage(
    channel="#file-content-test",
    text= text_id
  )


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def server():
    if request.method == 'GET':
        #print(request)
        return "si je change, ca passe?"  # Handle GET all Request
    elif request.method == 'POST':
        data = request.get_json(force=True)
        name = data['id']
        title = data ['title']
        print(name)
        print("downloading and sending")
        slackmsg(title)
        slackmsg(download(name))

        return "", 201  # Handle POST request

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000, debug=True)
    
