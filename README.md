# google-drive-concourse-resource

Uses google drive as a resource in concourse jobs/tasks as a way to pass output from 1 task to another in a given pipeline.

**Only supports tar and txt files for now**

**Uses modified Time for versioning so you always retrieve the latest file**

## Pre-Requisites

1. Follow this doc to create a service principal for the app to use and provide domain wide authority: https://developers.google.com/identity/protocols/OAuth2ServiceAccount#callinganapi
1. You will be using values from the JSON file you downloaded the step above to interact with your drive.
1. Create a folder on your google drive and provide the service principal you created access to edit that folder. This will be the folder where we will be doing gets/puts to.

## Source Configuration

* ``drive_client_email``: Required. The Client email for the service principal to use for drive interactions.

* ``drive_client_id``: Required. The client id of the service principal to use for drive interactions.

* ``drive_private_key_id``: Required. The private key id of the service principal to use for drive interactions.

* ``drive_private_key``: Required. The private key of the service principal to use for drive interactions.

* ``drive_folder_id``: Required. The folder **id** for all drive interactions. We are using ID and **NOT** the folder's name.

## Behavior

### ``check``: Extract versions from the

Currently we are returning the latest file's name based on modified Time of that file.

### ``in``: Download a file from google drive

We use the ``file_name`` to write the downloaded file on the local system. 

  * ``file_name``: The name of the latest version of the file that we need to fetch.

#### Parameters

None


### ``out``: Upload a file to google drive

Given a file specified by ``file_name`` parameter, upload it to a folder in google drive. Currently all uploads go to the root of the folder.

#### Parameters

* ``file_name``: Required. Path to the local file to upload to google drive

## Example Configuration

The following concourse pipeline downloads a file from github and uploads it to a folder on google drive. Then it downloads it again and prints that file.

```

---
resource_types:
- name: google-drive
  type: docker-image
  source:
    repository: jpatel4pivotal/google-drive-concourse-resource
jobs:
- name: test-put-gdrive-conc-resource
  serial: true
  plan:
  - get: source
    trigger: true
  - put: gdrive
    params:
      file_name: "/tmp/build/put/source/azure/ci/cloud_init_script.txt"

- name: test-get-gdrive-conc-resource
  serial: true
  plan:
  - get: gdrive
    passed: [test-put-gdrive-conc-resource]
    trigger: true
  - task: validate-file-from-gdrive
    config:
      platform: linux
      image_resource:
        type: docker-image
        source:
          repository: boogabee/datapeci
          tag: "latest"
      inputs:
      - name: gdrive
      run:
        path: sh
        args:
        - -exc
        - |
          ls -altrh gdrive
          cat gdrive/cloud_init_script.txt

resources:
- name: source
  type: git
  source:
    uri: {{git-uri}}
    branch: master
    username: {{git-user}}
    password: {{git-pass}}
- name: gdrive
  type: google-drive
  source:
    drive_client_email: {{gdrive_client_email}}
    drive_client_id: {{gdrive_client_id}}
    drive_private_key_id: {{gdrive_priv_key_id}}
    drive_private_key: {{gdrive_priv_key}}
    drive_folder_id: {{gdrive_folder_id}}

```
