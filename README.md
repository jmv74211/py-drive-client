# Py-drive client

![Status](https://img.shields.io/badge/Version-1.0-blue.svg)
![Status](https://img.shields.io/badge/Status-stable-green.svg)

Terminal client to manage files and directories from Google Drive.

- [Introduction](#introduction)
- [How to install](#how-to-install)
  * [Download or clone this repository](#download-or-clone-this-repository)
  * [Generate Google Drive API credentials file](#generate-google-drive-api-credentials-file)
  * [Install the `py-drive-client` app](#install-the--py-drive-client--app)
- [How to use](#how-to-use)
  * [List Google Drive files and directories](#list-google-drive-files-and-directories)
  * [Download files and directories from Google Drive](#download-files-and-directories-from-google-drive)
  * [Upload files and directories to Google Drive](#upload-files-and-directories-to-google-drive)
  * [Delete files from Google Drive](#delete-files-from-google-drive)

# Introduction

_Py-drive client_ is an application to manage files and directories from Google Drive.

Through terminal commands, the following actions can be performed:

- List Google Drive files and directories.
- Download files and directories from Google Drive to a local storage device.
- Upload files and directories from a local storage device to Google Drive.
- Delete files and directories from Google Drive.

This application has been tested on Linux and Windows.


# How to install

## Download or clone this repository

You can download the files and directories of this repository through the following link:
https://github.com/wazuh/wazuh/archive/refs/tags/v1.0.0.zip

You can also clone it using:

```
git clone https://github.com/jmv74211/py-drive-client.git
```

>Note: Be sure to download or clone the latest stable released version.

## Generate Google Drive API credentials file

First of all, you need to access the Google Drive API console from your Google account. You can access from here
https://console.cloud.google.com/apis/api/drive.googleapis.com

Next you will have to **enable** Google Drive API, create an `Oauth client` credentials and download them
using a `json` file. This file will have a name with the following regex `client_secret_*.json`.
**You must rename it to `client_secrets.json`**.

Finally, you must move or copy the file `client_secrets.json` to the following directory of
this app `src/py_drive_client/credentials`.

The final result should be as follows:

```
src/py_drive_client/credentials/client_secrets.json
```

## Install the `py-drive-client` app

Using a python version `>=3.6`, run the following command inside the root directory of this repository:

```
python3 setup.py install
```

Verify that it has been installed correctly and is accessible using the following command:

```
py-drive-client -h

usage: py-drive-client [-h] [-l <drive_path>] [-u <local_source_path> <drive_destination_path>] [-d <drive_object_path> <local_destination_path>] [-r <drive_path>] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -l <drive_path>, --list <drive_path>
                        List files from drive
  -u <local_source_path> <drive_destination_path>, --upload <local_source_path> <drive_destination_path>
                        Upload a file or folder from local to drive
  -d <drive_object_path> <local_destination_path>, --download <drive_object_path> <local_destination_path>
                        Download a file or folder from drive to local
  -r <drive_path>, --remove <drive_path>
                        Remove a file or folder from drive
  -v, --debug           Activate debug logging
```


# How to use

After installing the application, you can run it and view the available actions using:

```
py-drive-client -h
```

The following content will be displayed:

```
usage: py-drive-client [-h] [-l <drive_path>] [-u <local_source_path> <drive_destination_path>] [-d <drive_object_path> <local_destination_path>] [-r <drive_path>] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -l <drive_path>, --list <drive_path>
                        List files from drive
  -u <local_source_path> <drive_destination_path>, --upload <local_source_path> <drive_destination_path>
                        Upload a file or folder from local to drive
  -d <drive_object_path> <local_destination_path>, --download <drive_object_path> <local_destination_path>
                        Download a file or folder from drive to local
  -r <drive_path>, --remove <drive_path>
                        Remove a file or folder from drive
  -v, --debug           Activate debug logging
```

**Run the application for the first time**

> Note: Remember that before installing the application with the `setup.py` it is necessary to locate the
`client_secrets.json` file in the `src/py_drive_client/credentials` directory.

After running an application command for the first time, a browser window will open asking you to enter your Google
account credentials.

This is required to generate the user credentials file to provide access to the Google Drive account.

## List Google Drive files and directories

You can list any Google Drive path using the `-l` or `--list` parameter with the following syntax:

```
py-drive-client l <drive_path>
```

 >Note: The path of the content to be listed must be constructed in an absolute form

**Examples**

- List all files and directories in the Google Drive root:

  ```
  $ py-drive-client -l /

  2022-04-14 18:53:48,019 — INFO —  Drive files on path '/' = ['my_documents', 'images', 'music', 'example_file.jpg']
  ```

- List the contents of the `images` folder:

  ```
  $ py-drive-client -l /images

  2022-04-14 18:58:39,680 — INFO —  Drive files on path '/images' = ['family', 'friends', 'work']
  ```

## Download files and directories from Google Drive

You can download a file or directory with all its contents using the `-d` or `--download` parameter with the
following syntax:

```
py-drive-client -d <drive_object_path> <local_destination_path>
```

**Examples**

- Download the file `/example_file.jpg` to the local directory `/home/user/`.

  ```
  $ py-drive-client -d /example_file.jpg $HOME/example_file.jpg

  2022-04-14 19:11:52,002 — INFO —  Downloading '/example_file.jpg' from drive to '/home/user/example_file.jpg' local path
  ```

- Download the directory and its contents `/images/family` from Google Drive to the local directory
`/home/user/images/family`.

  ```
  $ py-drive-client -d /images/family $HOME/images/family

  2022-04-14 19:15:28,426 — INFO —  Downloading '/images/family' from drive to '/home/user/images/family' local path
  2022-04-14 19:15:30,368 — INFO —  Downloading '/images/family/photo_2.jpg' from drive to '/home/user/images/family/photo_2.jpg' local path
  2022-04-14 19:15:33,183 — INFO —  Downloading '/images/family/photo_1.jpg' from drive to '/home/user/images/family/photo_1.jpg' local path
  2022-04-14 19:15:35,833 — INFO —  Downloading '/images/family/photo_3.jpg' from drive to '/home/user/images/family/photo_3.jpg' local path
  2022-04-14 19:15:38,657 — INFO —  Downloading '/images/family/photo_5.jpg' from drive to '/home/user/images/family/photo_5.jpg' local path
  2022-04-14 19:15:41,193 — INFO —  Downloading '/images/family/photo_4.jpg' from drive to '/home/user/images/family/photo_4.jpg' local path
  ```

## Upload files and directories to Google Drive

You can upload a file or directory with all its contents using the `-u` or `--upload` parameter with the
following syntax:

```
py-drive-client -u  <local_source_path> <drive_destination_path>
```

**Examples**

- Upload the file `/home/user/example_file.jpg` to the Google Drive directory `my_documents`.

  ```
  $ py-drive-client -u $HOME/example_file.jpg /my_documets/example_file.jpg

  2022-04-15 13:09:23,924 — INFO —  Uploading '/home/user/example_file.jpg' from local path to /my_documets/example_file.jpg in drive
  ```

- Upload the directory `/home/user/images/family` to the Google Drive directory `/images/family`.

  ```
  $ py-drive-client -u $HOME/images/family /images/family

  2022-04-15 13:10:37,164 — INFO —  Uploading '/home/user/images/family' from local path to /images/family in drive
  2022-04-15 13:10:42,829 — INFO —  Uploading '/home/user/images/family/photo_3.jpg' from local path to /images/family/photo_3.jpg in drive
  2022-04-15 13:10:47,902 — INFO —  Uploading '/home/user/images/family/photo_2.jpg' from local path to /images/family/photo_2.jpg in drive
  2022-04-15 13:10:54,555 — INFO —  Uploading '/home/user/images/family/photo_4.jpg' from local path to /images/family/photo_4.jpg in drive
  2022-04-15 13:11:02,180 — INFO —  Uploading '/home/user/images/family/photo_1.jpg' from local path to /images/family/photo_1.jpg in drive
  2022-04-15 13:11:06,820 — INFO —  Uploading '/home/user/images/family/photo_5.jpg' from local path to /images/family/photo_5.jpg in drive
  ```

## Delete files from Google Drive

You can delete a file or directory from Google Drive using the `-r` or `--remove` parameter with the following syntax:

```
py-drive-client -r <drive_path>
```

**Examples**

- Delete the file `/my_documents/example_file.jpg` from Google Drive.

  ```
  $ py-drive-client -r /my_documents/example_file.jpg

  2022-04-15 13:15:58,534 — INFO —  Removing '/my_documents/example_file.jpg' from drive
  ```

- Delete the `/images/family` directory from Google Drive.

  ```
  $ py-drive-client -r /images/family

  2022-04-15 13:16:32,860 — INFO —  Removing '/images/family' from drive
  ```
