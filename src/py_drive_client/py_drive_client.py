"""
Author: @jmv74211

App to manage files in Google drive from local console. The following actions can be performed:

- List files in Google drive
- Upload files or directories to Google drive.
- Download files from Google drive to your storage unit.
- Delete files or directories from Google drive.

Requirements:
    - Have `client_secrets.json` file to access your Google Drive account through its API.

      This file will be used to authenticate and generate the `credentials.json` file needed to access your
      Google Drive account.

      To get the `client_secrets.json` file, you have to create a project in the Google API console, and get the
      OAuth client file.

      You can create a new project in the "API and services" section through the following URL
      https://console.cloud.google.com/
"""
import argparse
import logging
import sys
import os
import shutil

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

# ----------------------------------------------------------------------------------------------------------------------

CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'credentials')
DEFAULT_APP_CREDENTIALS_FILE = os.path.join(CREDENTIALS_PATH, 'client_secrets.json')
DEFAULT_USER_CREDENTIALS_FILE = os.path.join(CREDENTIALS_PATH, 'credentials.json')
LOGGER = logging.getLogger('py_drive')
COLORS = {
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'RED': '\033[91m',
    'END': '\033[0m'
}

# ------------------------------------------  PRIVATE FUNCTIONS  -------------------------------------------------------


def _error(message):
    """Log an ERROR message with a custom color (RED).

    Args:
        message (str): Logging message.
    """
    LOGGER.error(f"{COLORS['RED']}{message}{COLORS['END']}")


def _info(message):
    """Log an INFO message with a custom color (YELLOW).

    Args:
        message (str): Logging message.
    """
    LOGGER.info(f"{COLORS['YELLOW']} {message}{COLORS['END']}")  # Empty space before the message to align with others


def _debug(message):
    """Log a DEBUG message with a custom color (CYAN).

    Args:
        message (str): Logging message.
    """
    LOGGER.debug(f"{COLORS['CYAN']}{message}{COLORS['END']}")


def _set_logging(debug):
    """Define the app logger level and format.

    Args:
        debug (boolean): True to set a DEBUG level, False to set a INFO level.
    """
    LOGGER.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s — %(levelname)s — %(message)s"))
    LOGGER.addHandler(handler)


def _check_credentials_file():
    """Check if the app credentials file 'client_secrets.json' exist"""
    if not os.path.exists(DEFAULT_APP_CREDENTIALS_FILE):
        _error("Could not find the app credentials file 'client_secrets.json'")
        sys.exit(1)


def _get_parameters():
    """Get the user parameters when the app is run.

    Returns:
        argparse.Namespace: User parameters.
    """
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('-l', '--list', metavar=('<drive_path>'), type=str, required=False,
                            help='List files from drive')
    arg_parser.add_argument('-u', '--upload', metavar=('<local_source_path>', '<drive_destination_path>'),
                            type=str, nargs=2, required=False, help='Upload a file or folder from local to drive')
    arg_parser.add_argument('-d', '--download', metavar=('<drive_object_path>', '<local_destination_path>'),
                            type=str, nargs=2, required=False, help='Download a file or folder from drive to local')
    arg_parser.add_argument('-r', '--remove', metavar='<drive_path>', type=str, required=False,
                            help='Remove a file or folder from drive')
    arg_parser.add_argument('-v', '--debug', action='store_true', required=False, help='Activate debug logging')

    return arg_parser.parse_args()


def _validate_parameters(input_parameters):
    """Check if the user parameters are correct. If not, the execution will be stopped.

    Args:
        input_parameters (argparse.Namespace): User parameters.
    """
    _debug(f"Validating input parameters: {input_parameters}")
    parameters_value = [parameter for parameter in [input_parameters.upload, input_parameters.download,
                                                    input_parameters.list, input_parameters.remove]
                        if parameter is not None]

    # Check that there is no two different actions in the same command
    if len(parameters_value) > 1:
        _error('Select just one of the following actions: --list, --upload, --download or --remove')
        sys.exit(1)

    # Check that a required parameter value has been specified
    elif all(parameter is None for parameter in (input_parameters.upload, input_parameters.download,
             input_parameters.remove, input_parameters.list)):
        _error('Select one of the following actions: --list, --upload, --download or --remove')
        sys.exit(1)

    _debug('Parameters have been successfully validated')


def _drive_authentication(credentials_file=DEFAULT_USER_CREDENTIALS_FILE):
    """Get drive authentication using a credentials file.

    This process will load and validate the credentials file. If the credentials file does not exist or has expired,
    then a browser window will open to authenticate. After doing so, the credentials file will be generated.

    It is important that the `client_secrets.json` file is located in the same directory as the `py_drive_client.py`
    module. This file (`client_secrets.json`) is the credentials file for using the Google Drive API.

    Args:
        credentials_file (str): Path where the credential file is located.

    Returns:
        pydrive.auth.GoogleAuth: Drive authentication object
    """
    _debug('Authenticating with Drive API')
    google_auth = GoogleAuth()

    # Set app credentials path to the Google Auth object (needed when calling google_auth.LocalWebserverAuth())
    google_auth.DEFAULT_SETTINGS['client_config_file'] = DEFAULT_APP_CREDENTIALS_FILE

    # Load credentials file if exist
    if os.path.exists(credentials_file):
        google_auth.LoadCredentialsFile(credentials_file)

    # Create credentials if they dont exist
    if google_auth.credentials is None:
        _info('Could not find the credentials file. Generating a new one')
        google_auth.LocalWebserverAuth()
        google_auth.SaveCredentialsFile(credentials_file)
        _info('Credentials file have been saved successfully')
    # Renew credentials if they are expired
    elif google_auth.access_token_expired:
        _info('The credentials token has expired. Generating a new one')
        google_auth.Refresh()
        google_auth.SaveCredentialsFile(credentials_file)
        _info('Credentials file have been saved successfully')
    else:
        google_auth.Authorize()

    _debug('Successfully authenticated')

    return google_auth


def _is_drive_dir(object_data):
    """Check if the object is a Google Drive directory.

    Args:
        object_data (pydrive.files.GoogleDriveFile): Google Drive file object data.

    Returns:
        boolean: True if the object is a directory, False otherwise.
    """
    return object_data['mimeType'] == 'application/vnd.google-apps.folder'


def _get_drive_object(drive, path):
    """Get the drive data from a specific object. If the path is /, then it gets all the information about the
    files and directories in /, otherwise, it obtains the data of the specified object.

    Args:
        drive (pydrive.drive.GoogleDrive): Google Drive instance object.
        path (str): Google drive path to get the object.

    Returns:
        list(GoogleDriveFile): List with object information (1 item if path is not /)
    """
    _debug(f"Getting file info for '{path}'")
    path = path[1:] if path and path[0] == '/' else path  # Clean initial /
    tree = path.split('/')
    drive_objects = []

    # If queried about root path, then return root data
    if path == '':
        _debug('Single path detected (root)')
        drive_objects = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    # If path level is greater than 0, then walk through the directories structure
    else:
        _debug(f"Compound path detected ({path})")
        for level, path_name in enumerate(tree):
            if level == 0:
                drive_objects = drive.ListFile({'q': f"'root' in parents and title='{path_name}' and \
                                            trashed=false"}).GetList()
            else:
                # If no data was obtained in the previous iteration, then return empty to indicate that no data exists.
                if len(drive_objects) == 0:
                    _debug(f"{path_name} was not found in drive")
                    return []

                drive_objects = drive.ListFile({'q': f"'{drive_objects[0]['id']}' in parents and title='{path_name}' \
                                             and trashed=false"}).GetList()
    return drive_objects


def _path_exist_in_drive(drive, path):
    """Check if the specified path exist in Google Drive.

    Args:
        drive (pydrive.drive.GoogleDrive): Google Drive instance object.
        path (str): Google drive path to check.

    Returns:
        boolean: True if exists, False otherwhise.
    """
    _debug(f"Checking if '{path}' path exists in drive")
    exist = len(_get_drive_object(drive, path)) > 0
    _debug(f"'{path}' path {'exists' if exist else 'does not exist'} in drive")

    return exist


def _create_drive_path(drive, path):
    """Create the specified path in the Google Drive if it does not exist.

    Args:
        drive (pydrive.drive.GoogleDrive): Google Drive instance object.
        path (str): Google drive path to create.
    """
    if not _path_exist_in_drive(drive, path):
        _debug(f"Creating '{path}' path in drive")
        path = path[1:] if path and path[0] == '/' else path  # Clean initial /
        tree = path.split('/')
        drive_objects = _get_drive_object(drive, path='/')
        path_built = ''

        for path_name in tree:
            # If the path name is not contained in the current path, then create it
            if path_name not in [item['title'] for item in drive_objects]:
                path_id = 'root' if path_built == '' else _get_drive_object(drive, path_built)[0]['id']
                folder = drive.CreateFile({'parents': [{'id': path_id}], 'title': path_name,
                                           'mimeType': 'application/vnd.google-apps.folder'})
                folder.Upload()

            path_built += f"/{path_name}"
            drive_objects = get_drive_objects(drive, path_built)

        _debug(f"'{path}' path has been created in drive")


def _create_local_path(local_path):
    """Create the specified path in the local storage unit if it does not exist.

    Args:
        local_path (str): Local path to create.
    """
    if not os.path.exists(local_path):
        _debug(f"Creating '{local_path}' path in local")
        os.makedirs(local_path)


def _process_request(drive, input_parameters):
    """Process the action to be performed by the app taking into account the input parameters.

    Args:
        drive (pydrive.drive.GoogleDrive): Google Drive instance object.
        input_parameters (argparse.Namespace): Input parameters.
    """
    if input_parameters.list is not None:
        if not _path_exist_in_drive(drive, input_parameters.list):
            _error(f"The '{input_parameters.list}' path does not exist in Google Drive")
            sys.exit(1)
        drive_file_names = get_drive_object_names(drive, input_parameters.list)
        _info(f"Drive files on path '{input_parameters.list}' = {drive_file_names}")
    elif input_parameters.upload is not None:
        upload_objects_to_drive(drive, input_parameters.upload[0], input_parameters.upload[1])
    elif input_parameters.download is not None:
        download_drive_objects(drive, input_parameters.download[0], input_parameters.download[1])
    elif input_parameters.remove is not None:
        remove_drive_objects(drive, input_parameters.remove)

# -------------------------------------------  PUBLIC FUNCTIONS  -------------------------------------------------------


def get_drive_objects(drive, path):
    """Get all the Google Drive objects from the specified path.

    Args:
        drive (pydrive.drive.GoogleDrive): Google Drive instance object.
        path (str): Google drive path to get its objects.

    Returns:
        list(GoogleDriveFile): Google Drive object list.
    """
    _debug(f"Getting files and directories from '{path}' path")

    # If root path, then the called function will return all the root objects
    if path == '/':
        return _get_drive_object(drive, path)

    # Get the drive object data
    drive_object = _get_drive_object(drive, path)
    drive_objects = drive_object

    # If Google Drive specified path does not exist
    if len(drive_objects) == 0:
        return []

    # If directory, then go inside and get the information of its content
    if _is_drive_dir(drive_objects[0]):
        drive_objects = drive.ListFile({'q': f"'{drive_objects[0]['id']}' in parents and trashed=false"}).GetList()

    return drive_objects


def get_drive_object_names(drive, path):
    """Get the names of all Google Drive objects in the specified directory.

    Args:
        drive (pydrive.drive.GoogleDrive): Google Drive instance object.
        path (str): Google drive path to get its objects.

    Returns:
        list(str): List of object names.
    """
    return [file_name['title'] for file_name in get_drive_objects(drive, path)]


def upload_objects_to_drive(drive, local_path, drive_path, create_directories=True):
    """Upload a file or local directory with all its contents (recursive) to Google Drive.

    Args:
        drive (pydrive.drive.GoogleDrive): Google Drive instance object.
        local_path (str): Local path to upload to Google Drive.
        drive_path (str): Google Drive path where the file or directory will be uploaded.
        create_directories (boolean): True to check if it is needed to create directories, False otherwise.
    """
    _info(f"Uploading '{local_path}' from local path to {drive_path} in drive")

    if not os.path.exists(local_path):
        _error(f"'{local_path}' local path does not exists")
        sys.exit(1)

    if _path_exist_in_drive(drive, drive_path):
        _error(f"'{drive_path}' path already exists on drive")
        sys.exit(1)

    base_name = os.path.basename(drive_path)
    path_name = os.path.dirname(drive_path)

    if os.path.isfile(local_path):
        if create_directories:
            _create_drive_path(drive, path_name)  # Create drive path if not exist (check is made inside the function)

        path_id = _get_drive_object(drive, path_name)[0]['id']

        file = drive.CreateFile({'parents': [{'id': path_id}], 'title': base_name})
        file.SetContentFile(local_path)
        file.Upload()

    elif os.path.isdir(local_path):
        _create_drive_path(drive, drive_path)  # Create drive path if not exist (check is made inside the function)
        path_id = _get_drive_object(drive, path_name)[0]['id']

        for item in os.listdir(local_path):
            item_path = f"{local_path}/{item}"
            # Recursive calls to create and copy the files tree
            if os.path.isfile(item_path):
                # Avoid check drive directories, because all these elements have the same
                # parent folder, and it is already created (lightweight calls).
                upload_objects_to_drive(drive, item_path, f"{drive_path}/{item}", False)
            elif os.path.isdir(item_path):
                upload_objects_to_drive(drive, item_path, f"{drive_path}/{item}")
    else:
        _error(f"Local path {local_path} is not detected as file or directory")
        sys.exit(1)


def download_drive_objects(drive, drive_path, local_path, check_remote_exist=True):
    """Download a Google Drive file or directory (with all its content) to the specified local path.

    Args:
        drive (pydrive.drive.GoogleDrive): Google Drive instance object.
        drive_path (str): Google Drive path where the file or directory will be downloaded.
        local_path (str): Local path where locate the downloaded files.
        check_remote_exist (boolean): True to check if drive path exists, False otherwise.
    """
    # Set the current working directory if selected the '.' or './' characters
    local_path = f"{os.getcwd()}/{os.path.basename(drive_path)}" if local_path == '.' or local_path == './' else \
        local_path

    if os.path.exists(local_path):
        _error(f"The '{local_path}' local path already exists")
        sys.exit(1)

    # Necessary to check only the first time, because in recursive calls we know that it will exist.
    if check_remote_exist:
        if not _path_exist_in_drive(drive, drive_path):
            _error(f"The '{drive_path}' path does not exist in Google Drive")
            sys.exit(1)

    _info(f"Downloading '{drive_path}' from drive to '{local_path}' local path")

    drive_object = _get_drive_object(drive, drive_path)[0]

    if _is_drive_dir(drive_object):
        _create_local_path(local_path)
        drive_objects = get_drive_objects(drive, drive_path)

        for _object in drive_objects:
            if _is_drive_dir(_object):
                download_drive_objects(drive, f"{drive_path}/{_object['title']}", f"{local_path}/{_object['title']}",
                                       False)
            else:
                download_drive_objects(drive, f"{drive_path}/{_object['title']}", f"{local_path}/{_object['title']}",
                                       False)
    else:
        file_base_name = os.path.basename(drive_path)
        file = drive.CreateFile({'id': drive_object['id']})
        file.GetContentFile(file_base_name)

        # Create dirname path if it does not exist
        _create_local_path(os.path.dirname(local_path))

        # Move the downloaded file to its destination path
        shutil.move(file_base_name, local_path)


def remove_drive_objects(drive, drive_path, trash=True):
    """Remove a remote Google Drive object.

    Args:
        drive (pydrive.drive.GoogleDrive): Google Drive instance object.
        drive_path (str): Google Drive path to remove.
        trash (boolean): True if the removed file or directory will be sent to the trash, False to remove it
                         permanently.
    """
    if _path_exist_in_drive(drive, drive_path):
        object_id = _get_drive_object(drive, drive_path)[0]['id']
        _object = drive.CreateFile({'id': object_id})

        _info(f"Removing '{drive_path}' from drive")

        # Remove the parent object
        _object.Trash() if trash else _object.Delete()
    else:
        _error(f"Could not remove the '{drive_path}' from drive, it does not exist")


# -------------------------------------------------  MAIN  -------------------------------------------------------------


def main():
    """Main process:
        - Get the input parameters.
        - Validate parameters.
        - Check credentials file.
        - Authenticate the request and process it.
    """
    input_parameters = _get_parameters()
    _set_logging(input_parameters.debug)
    _validate_parameters(input_parameters)
    _check_credentials_file()
    drive = GoogleDrive(_drive_authentication())
    _process_request(drive, input_parameters)


if __name__ == "__main__":
    main()
