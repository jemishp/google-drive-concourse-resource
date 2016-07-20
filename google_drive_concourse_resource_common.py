#!/usr/local/bin/python
from __future__ import print_function
import os,sys
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient.discovery import build
from apiclient import errors
from apiclient import http


def getServiceInstance(sEmail, pID, cID, pKey,verbose=False):
    """Creates an authenticated service instance to use for subsequent requests to google drive
    Args:
        sEmail: client_email to use for service account credentials to authenticate with google drive
        pID: private key id to use for service account credentials to authenticate with google drive
        cID: client_id to use for service account credentials to authenticate with google drive
        pKey: private key to use for service account credentials to authenticate with google drive
    Returns:
        An authenticated service instance of google drive v2 API
    """

    scopes = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.file']
    key_dict = {'type':'service_account','client_email': sEmail, 'private_key_id':pID , 'client_id': cID, 'private_key': pKey}
    if verbose:
        print (str(key_dict),file=sys.stderr)
        ##Adding a debug print for testing
        #print(dir(ServiceAccountCredentials))


    credentials = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scopes=scopes)
    # Impersonate a user
    #delegated_credentails = credentials.create_delegated(user + '@pivotal.io')
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
        print('Query = ' + folderID + ' in parents and name = ' + fileName + '',file=sys.stderr)


    results = drive_service.files().list(q="'" + folderID + "' in parents and title = '" + fileName + "'",
                                        corpus='DEFAULT',
                                        spaces='drive',
                                        maxResults=10).execute()
    if verbose:
        print(results,file=sys.stderr)
    items = results.get('items', [])
    if not items:
        print('No files found.', file=sys.stderr)
        return None
    else:
        #print('Files:')
        for item in items:
            print('{0} ({1}) {2}'.format(item['title'], item['id'], item['mimeType']),file=sys.stderr)
            fileFound = item
        return fileFound

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
    print ('Folder Name: {0} ID: {1}' .format(file.get('title'), file.get('id')),file=sys.stderr)

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

    # Getting Env info to use for metadata tagging

    atc = os.getenv('ATC_EXTERNAL_URL','DEFAULT_ATC')
    pipe = os.getenv('BUILD_PIPELINE_NAME','DEFAULT_PIPELINE')
    job = os.getenv('BUILD_JOB_NAME','DEFAULT_JOB')
    build = os.getenv('BUILD_NAME','DEFAULT_BUILD_NUM')

    # Creteing a link URL to put in metadata
    link = atc + '/pipelines/' + pipe + '/jobs/' + job + '/builds/' + build

    media_body = http.MediaFileUpload(filePath,mimetype=mime_type,resumable=True)
    body = {
      'title': f,
      'description': 'Uploaded by concourse task: \n\n' + link + '',
      'mimeType': mime_type
    }
    # Set the parent Folder
    if folderID:
        body['parents'] = [{'id': folderID}]
        #Temporarily adding perms here
        #body['permissions'] = perms

    if verbose:
        #print('Body: ' .format(dir(body)))
        print('Body: {0}' .format(body),file=sys.stderr)

    try:
        file = drive_service.files().insert(
                                            body=body,
                                            media_body=media_body).execute()
        #Printing for debug only
        #print ('File ID {0} ' .format(file.get('id')))
        return file
    except errors.HttpError, error:
        #print 'An error occured: %s' % error
        return error


# Commenting out as we don't need this
# def getPermissions(service, file_id):
#     """Retrieve a list of permissions.
#     Args:
#     service: Drive API service instance.
#     file_id: ID of the file to retrieve permissions for.
#     Returns:
#     List of permissions.
#     """
#     try:
#         permissions = service.permissions().list(fileId=file_id).execute()
#         return permissions.get('items', [])
#     except errors.HttpError, error:
#         print ('An error occurred: {0}' .format(error))
#         return error

def getFile(service, folderID, fileID, fileName, verbose=False):
    """Retrieves a File from a google drive Folder. Currently we only
    support binary files so you can not get docs,spreadhseets, etc.
    Args:
        service: google drive service instance to use
        folderID: Parent Folder's ID from which to get the file
        fileID: Id of the file that needs to be retrieved from google drive
        fileName: Name to use for the local file
        verbose: print debugging information
    Returns:
        File that was requested or error if error occured
    To Do:
        Check if File and folder exist
        Possible check if File is not 0 length before putting it up on google drive
    """
    drive_service=service
    local_fd=open(fileName,'w')
    if verbose:
        print('Received FileID = ' + fileID , file=sys.stderr)

    request = drive_service.files().get_media(fileId=fileID)

    if verbose:
        print('Headers: {0}' .format(request.headers),file=sys.stderr)
        print('URI: {0}' .format(request.uri),file=sys.stderr)

    media_request = http.MediaIoBaseDownload(local_fd, request)

    while True:
        try:
          download_progress, done = media_request.next_chunk()
        except errors.HttpError, error:
          #print 'An error occurred: %s' % error
          return error
        if download_progress:
          print('Download Progress: %d%%' % int(download_progress.progress() * 100), file=sys.stderr)
        if done:
          #print 'Download Complete'
          return
