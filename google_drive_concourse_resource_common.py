#!/usr/local/bin/python
import os
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient.discovery import build
from apiclient import errors
from apiclient import http


def getServiceInstance(user='jpatel', keyFile='concourse-resource.json'):
    """Creates an authenticated service instance to use
    Args:
        user: User to impersonate in requests
        keyFile: file that has the service account credentials
    Returns:
        An authenticated service instance
    """

    scopes = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(keyFile, scopes=scopes)
    # Impersonate a user
    delegated_credentails = credentials.create_delegated(user + '@pivotal.io')
    # Apply credential headers to all requests made by an an httlib2.Http instance
    http_auth = credentials.authorize(Http())
    # Build a service object for the drive API with the authenticated http instance
    gdriveservice = build('drive', 'v2', http=http_auth)

    oldq='0B_rb6msCq2WfSVk2QVl6UUk5cFk' # skahler's private folder with no access
    return gdriveservice

def listFilesinFolder(service, folderID, fileName, verbose=False):
    """Searches a google drive folder for a file
    Args:
        service: google drive service instance to use
        folderID: the folder to lok for the file in
        fileName: name of the file to search for
        verbose: print debugging information
    Returns:
        File ID of the file was found and none if it was not
    """

    drive_service=service

    if verbose:
        print('Query = ' + folderID + ' in parents and name = ' + fileName + '')


    results = drive_service.files().list(q="'" + folderID + "' in parents and title = '" + fileName + "'",
                                        corpus='DEFAULT',
                                        spaces='drive',
                                        maxResults=10).execute()
    if verbose:
        print(results)
    items = results.get('items', [])
    if not items:
        print('No files found.')
        return None
    else:
        print('Files:')
        for item in items:
            print('{0} ({1}) {2}'.format(item['title'], item['id'], item['mimeType']))
        return item['id']

def create_folder(service, folderName, parentID = None):
    """Creates a folder to use.
    Args:
        service: google drive service instance to use
        parentID: Parent folder's ID in which to create the new folder
        folderName: name to use for the new folder
    Returns:
        Folder Name and ID of the newly created folder
    """
    drive_service=service
    body = {
        'title' : folderName,
        'mimeType' : 'application/vnd.google-apps.folder'
    }
    if parentID:
        body['parents'] = [{'id': parentID}]
    file = drive_service.files().insert(body=body).execute()
    print ('Folder Name: {0} ID: {1}' .format(file.get('title'), file.get('id')))

def putFile(service, folderID, filePath, verbose=False):
    """Creates a File on a google drive folder.
    Args:
        service: google drive service instance to use
        folderID: Parent Folder's ID in which to create the new file
        filePath: Path to the file that needs to be put on google drive
        verbose: print debugging information
    Returns:
        File name and ID of the newly created File or error if error occured
    To Do:
        Check if File and folder exist
        Possible check if File is not 0 length before putting it up on google drive
    """
    drive_service=service
    f=os.path.basename(filePath)
    mime_type=''

    media_body = http.MediaFileUpload(filePath,mimetype=mime_type,resumable=True)
    body = {
      'title': f,
      'description': 'Test',
      'mimeType': mime_type
    }
    # Set the parent Folder
    if folderID:
        body['parents'] = [{'id': folderID}]
        #Temporarily adding perms here
        body['permissions'] = [{'role': 'owner','type': 'domain'}]

    if verbose:
        #print('Body: ' .format(dir(body)))
        print('Body: {0}' .format(body))

    try:
        file = drive_service.files().insert(
                                            body=body,
                                            media_body=media_body).execute()
        #Printing for debug only
        print ('File ID {0} ' .format(file.get('id')))
        return file
    except errors.HttpError, error:
        print 'An error occured: %s' % error
        return error

def getFile(service, folderID, fileID, verbose=False):
    """Retrieves a File from a google drive Folder. Currently we only
    support binary files so you can not get docs,spreadhseets, etc.
    Args:
        service: google drive service instance to use
        folderID: Parent Folder's ID from which to get the file
        fileID: Id of the file that needs to be retrieved from google drive
        verbose: print debugging information
    Returns:
        File that was requested or error if error occured
    To Do:
        Check if File and folder exist
        Possible check if File is not 0 length before putting it up on google drive
    """
    drive_service=service

    if verbose:
        print('Received FileID = ' + fileID )

    request = drive_service.files().get_media(fileId=fileID)

    if verbose:
        print('Headers: {0}' .format(request.headers))
        print('URI: {0}' .format(request.uri))

    media_request = http.MediaIoBaseDownload('test.txt', request)

    while True:
        try:
          download_progress, done = media_request.next_chunk()
        except errors.HttpError, error:
          print 'An error occurred: %s' % error
          return error
        if download_progress:
          print 'Download Progress: %d%%' % int(download_progress.progress() * 100)
        if done:
          print 'Download Complete'
          return
