from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

try:
    #Creating an empty dataframe
    result = []
    
    service = build('drive', 'v3', credentials=creds)
    
    #Parent Folder Details
    folder_name = '' #Example: 'test'
    folder_id = '11qeWq4FtIGfSjt-PB5EnDxz067FFkYQx' #Example: '11qeWq4FtIGfSjt-PB5EnDxz0s7FFkYyx
    
    #DFS
    res= []
    
    def helper(folder_id, folder_name):
        
        res.append((folder_name,folder_id))
        
        query = f"parents='{folder_id}'"
        response = service.files().list(q=query).execute()
        files = response.get('files')
        nextPageToken = response.get('nextPageToken')
        
        while nextPageToken:
            response = service.files().list(q=query).execute()
            files.extend(response.get('files'))
            nextPageToken = response.get('nextPageToken')
        
        if not response:
            return
        
        #Base Case
        if not files: 
            if not res[-1]:
                return
            result.append(res.copy())
            return 
        
        for file in files:
            helper(file['id'],file['name'])
            res.pop(-1)
            
    helper(folder_id,folder_name)
    df = pd.DataFrame(result)
    
    #Save the file
    df.to_csv('all_files.csv')
    
except HttpError as error:
    print(f'An error occurred: {error}')
