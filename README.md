# google-drive-concourse-resource

Uses google drive as a resource in concourse jobs/tasks as a way to pass output from 1 task to another in a given pipeline.

**Only supports tar and txt files for now**

**Does not do any version checking**

# Pre-Requisites

1. Follow this doc to create a service principal for the app to use and provide domain wide authority: https://developers.google.com/identity/protocols/OAuth2ServiceAccount#callinganapi
1. You will be using values from the JSON file you downloaded the step above to interact with your drive.

# Source Configuration

* ``google_drive_client_email``: Required. The Client email for the service principal to use for drive interactions.

* ``google_drive_client_id``: Required. The client id of the service principal to use for drive interactions.

* ``google_drive_private_key_id``: Required. The private key id of the service principal to use for drive interactions.

* ``google_drive_private_key``: Required. The private key of the service principal to use for drive interactions.

* ``google_drive_folder_id``: Required. The folder **id** for all drive interactions. We are using ID and **NOT** the folder's name.

# Behavior

``check``: Extract versions from the

Currently we are returning nulls for versioned objects.

``in``: Download a file from google drive

``out``: Upload a file to google drive
