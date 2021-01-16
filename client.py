import os
import shutil

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

# ----------------------------------------------------------------------------------------------------------------------

CREDENTIALS_FILE = 'credentials.json'
VERBOSE = True
TEXT_COLOR = True

COLORS = {
    'OK': '\033[92m',
    'WARNING': '\033[93m',
    'ERROR': '\033[91m',
    'END': '\033[0m'
}

# ----------------------------------------------------------------------------------------------------------------------
#                                                  AUX FUNCTIONS                                                       #
# ----------------------------------------------------------------------------------------------------------------------


def action_verbose(message):
    """
    Print an action in console output if verbose option is activated

    Parameters
    ----------
    message: str
        Action message to print
    """

    if VERBOSE:
        print(message, end='', flush=True)

# ----------------------------------------------------------------------------------------------------------------------


def action_status_verbose(status='OK'):
    """
    Print the action result in console output

    Parameters
    ----------
    status: str
        Action status
    """

    if TEXT_COLOR:
        print(f" ... {COLORS[status]}{status}{COLORS['END']}")
    else:
        print(f" ... {status}")

# ----------------------------------------------------------------------------------------------------------------------


def error_verbose(message):
    """
    Print an error in console output. If text color option is activated, the color message will be red

    Parameters
    ----------
    message: str
        Error message to print
    """

    if TEXT_COLOR:
        print(f"{COLORS['ERROR']}ERROR: {message}{COLORS['END']}")
    else:
        print(f"ERROR: {message}")

# ----------------------------------------------------------------------------------------------------------------------


def create_local_path(local_path):
    """
    Create a local folder path if not exists

    Parameters
    ----------
    local_path: str
        Local path to create. Example: /home/user/test
    """

    if os.path.exists(local_path):
        action_verbose(f"'{local_path}' local path already exists. Exiting...")
        return

    os.makedirs(local_path)

# ----------------------------------------------------------------------------------------------------------------------
#                                                  DRIVE FUNCTIONS                                                     #
# ----------------------------------------------------------------------------------------------------------------------


def is_drive_dir(file_data):
    """
    Check if a drive object is a directory

    Parameters
    ----------
    file_data: pydrive.files.GoogleDriveFile
        Local path to create. Example: /home/user/test

    Returns
    -------
    Boolean
        True if drive file object is a folder, False otherwise
    """

    return file_data['mimeType'] == 'application/vnd.google-apps.folder'

# ----------------------------------------------------------------------------------------------------------------------


def path_exist_in_drive(path):
    """
    Check if an specific path exists in drive

    Parameters
    ----------
    path: pydrive.files.GoogleDriveFile
        Local path to create. Example: /home/user/test

    Returns
    -------
    Boolean
        True if drive path exists, False otherwise
    """

    return len(get_drive_files(path)) > 0

# ----------------------------------------------------------------------------------------------------------------------


def authenticate(credentials_file):
    """
    Get drive authentication using a credentials file

    Parameters
    ----------
    credentials_file: str
        Path string where credentials_files is located

    Returns
    -------
    pydrive.auth.GoogleAuth
        Drive authentication object
    """

    action_verbose('Authenticating request')
    google_auth = GoogleAuth()
    google_auth.LoadCredentialsFile(credentials_file)

    if google_auth.credentials is None:
        google_auth.LocalWebserverAuth()
    elif google_auth.access_token_expired:
        google_auth.Refresh()
    else:
        google_auth.Authorize()

    google_auth.SaveCredentialsFile(credentials_file)
    action_status_verbose()
    print(type(google_auth))

    return google_auth

# ----------------------------------------------------------------------------------------------------------------------


def get_drive_files(path):
    """
    Get the file object info from a specific drive path

    Parameters
    ----------
    path: str
        Drive path to find the file object

    Returns
    -------
    List<pydrive.files.GoogleDriveFile>
        File info list. Usually this list only contains one element
    """

    if path and path[0] == '/':
        path = path[1:]

    tree = path.split('/')
    file_data = None

    if not path:
        file_data = drive.ListFile({'q': f"'root' in parents and trashed=false"}).GetList()
    else:
        # Walk through the directories structure
        for idx, path_name in enumerate(tree):
            if(idx == 0):
                file_data = drive.ListFile({'q': f"'root' in parents and title='{path_name}' and \
                                             trashed=false"}).GetList()
            else:
                # If path not found, then leave and return empty list
                if not file_data:
                    return []

                file_data = drive.ListFile({'q': f"'{file_data[0]['id']}' in parents and title='{path_name}' \
                                             and trashed=false"}).GetList()

    return file_data

# ----------------------------------------------------------------------------------------------------------------------


def list_drive_files(path):
    """
    Get all files object info from a specific path (Returns all the information of the files contained in a directory)

    Parameters
    ----------
    path: str
        Drive path to list all files

    Returns
    -------
    List<pydrive.files.GoogleDriveFile>
        File info list.
    """

    files = get_drive_files(path)

    if len(files) == 0:
        return []

    # If directory, then go inside and get the information of its content
    if is_drive_dir(files[0]):
        files = drive.ListFile({'q': f"'{files[0]['id']}' in parents and trashed=false"}).GetList()

    return files

# ----------------------------------------------------------------------------------------------------------------------


def create_drive_path(path):
    """
    Function to create a drive folder path if not exists

    Parameters
    ----------
    path: str
        Path to create in drive
    """

    if not path_exist_in_drive(path):
        action_verbose(f"Creating '{path}' path in drive")
        if path and path[0] == '/':
            path = path[1:]

        tree = path.split('/')
        files = get_drive_files('/')

        path_built = ''

        for path_name in tree:
            if path_name not in [item['title'] for item in files]:
                path_id = 'root'

                if path_built:
                    path_id = get_drive_files(path_built)[0]['id']

                folder = drive.CreateFile({'parents': [{'id': path_id}], 'title': path_name,
                                           'mimeType': 'application/vnd.google-apps.folder'})
                folder.Upload()

            path_built += f'/{path_name}'
            files = list_drive_files(path_built)

        action_status_verbose()

# ----------------------------------------------------------------------------------------------------------------------


def upload_files_to_drive(local_path, drive_path, create_directories=True):
    """
    Upload an specific file or a folder with its content to drive

    Parameters
    ----------
    local_path: str
        Local path where is located the file or folder to upload
    drive_path: str
        Drive path where upload the folder or file. If this drive path not exists, then it is created automatically
    create_directories: boolean
        Flag to avoid create the drive path. Useful when we are copying files with a known drive folder
    """

    if path_exist_in_drive(drive_path):
        error_verbose(f"'{drive_path}' path already exists on drive. Exiting...")
        return

    if not os.path.exists(local_path):
        error_verbose(f"'{local_path}' local path does not exists. Exiting...")
        return

    base_name = os.path.basename(drive_path)
    path_name = os.path.dirname(drive_path)

    if os.path.isfile(local_path):
        if create_directories:
            create_drive_path(path_name)

        path_id = get_drive_files(path_name)[0]['id']

        action_verbose(f"Uploading {local_path} file to {drive_path}")
        file = drive.CreateFile({'parents': [{'id': path_id}], 'title': base_name})
        file.SetContentFile(local_path)
        file.Upload()
        action_status_verbose()

    elif os.path.isdir(local_path):
        create_drive_path(drive_path)
        path_id = get_drive_files(drive_path)[0]['id']

        for item in os.listdir(local_path):
            item_path = f"{local_path}/{item}"
            if os.path.isfile(item_path):
                # Avoid check drive directories, because all these elements have the same
                # parent folder, and it is already created (lightweight calls).
                upload_files_to_drive(item_path, f"{drive_path}/{item}", False)
            elif os.path.isdir(item_path):
                upload_files_to_drive(item_path, f"{drive_path}/{item}")
    else:
        error_verbose(f"Local path {local_path } is not detected as file or directory. Exiting...")

# ----------------------------------------------------------------------------------------------------------------------


def download_drive_files(drive_path, local_path):
    """
    Download a drive file or folder with its content to local path

    Parameters
    ----------
    drive_path: str
        Drive path where is located the file or folder to download
    local_path: str
        Local path where save the downloaded files
    """

    if not path_exist_in_drive(drive_path):
        error_verbose(f"'{drive_path}' do not exists in drive. Exiting...")
        return

    if os.path.exists(local_path):
        error_verbose(f"'{local_path}' already exists in local path. Exiting...")
        return

    drive_file = get_drive_files(drive_path)[0]
    file_id = drive_file['id']

    if is_drive_dir(drive_file):
        create_local_path(local_path)
        files = list_drive_files(drive_path)

        for file in files:
            if is_drive_dir(file):
                download_drive_files(f"{drive_path}/{file['title']}", f"{local_path}/{file['title']}")
            else:
                download_drive_files(f"{drive_path}/{file['title']}", f"{local_path}/{file['title']}")
    else:
        file_base_name = os.path.basename(drive_path)

        action_verbose(f"Downloading {drive_path} file to {local_path}")
        file = drive.CreateFile({'id': file_id})
        file.GetContentFile(file_base_name)
        shutil.move(file_base_name, local_path)
        action_status_verbose()

# ----------------------------------------------------------------------------------------------------------------------
#                                                      MAIN                                                            #
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    google_auth = authenticate(CREDENTIALS_FILE)
    drive = GoogleDrive(google_auth)
