import os
import shutil

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

# ----------------------------------------------------------------------------------------------------------------------

CREDENTIALS_FILE = 'credentials.json'
VERBOSE = True

# ----------------------------------------------------------------------------------------------------------------------


def authenticate(credentials_file):
    verbose("Authenticating request...")
    google_auth = GoogleAuth()
    google_auth.LoadCredentialsFile(credentials_file)

    if google_auth.credentials is None:
        google_auth.LocalWebserverAuth()
    elif google_auth.access_token_expired:
        google_auth.Refresh()
    else:
        google_auth.Authorize()

    google_auth.SaveCredentialsFile(credentials_file)
    verbose("Authentication successfull")
    return google_auth

# ----------------------------------------------------------------------------------------------------------------------


def is_drive_dir(file_data):
    return file_data['mimeType'] == 'application/vnd.google-apps.folder'

# ----------------------------------------------------------------------------------------------------------------------


def verbose(message):
    if VERBOSE:
        print(message)

# ----------------------------------------------------------------------------------------------------------------------

def get_files(path):
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


def list_files(path):
    files = get_files(path)

    if len(files) == 0:
        return []

    # If directory, then go inside and get the information of its content
    if is_drive_dir(files[0]):
        files = drive.ListFile({'q': f"'{files[0]['id']}' in parents and trashed=false"}).GetList()

    return files

# ----------------------------------------------------------------------------------------------------------------------


def path_exist(path):
    return len(get_files(path)) > 0

# ----------------------------------------------------------------------------------------------------------------------


def create_drive_path(path):
    print("111111")
    if not path_exist(path):
        print("2222222222")
        if path and path[0] == '/':
            path = path[1:]

        tree = path.split('/')
        files = get_files('/')

        path_built = ''

        for path_name in tree:
            if path_name not in [item['title'] for item in files]:
                path_id = 'root'

                if path_built:
                    path_id = get_files(path_built)[0]['id']

                folder = drive.CreateFile({'parents': [{'id': path_id}], 'title': path_name,
                                           'mimeType': 'application/vnd.google-apps.folder'})
                folder.Upload()

            path_built += f'/{path_name}'
            files = list_files(path_built)

        verbose(f"Created path --> {path}")

# ----------------------------------------------------------------------------------------------------------------------

def create_local_path(local_path):
    if os.path.exists(local_path):
        print(f"{local_path} path already exists. Exiting...")
        return

    os.makedirs(local_path)

# ----------------------------------------------------------------------------------------------------------------------


def upload_files(local_path, drive_path, create_directories=True):
    if path_exist(drive_path):
        verbose("The folder or file path already exists. Exiting...")
        return

    if not os.path.exists(local_path):
        verbose(f"{local_path} does not exist. Exiting...")
        return

    base_name = os.path.basename(drive_path)
    path_name = os.path.dirname(drive_path)

    if os.path.isfile(local_path):
        if create_directories:
            create_drive_path(path_name)

        path_id = get_files(path_name)[0]['id']

        verbose(f"Uploading {local_path} file to {drive_path}")
        file = drive.CreateFile({'parents': [{'id': path_id}], 'title': base_name})
        file.SetContentFile(local_path)
        file.Upload()
        verbose(f"File {drive_path} uploaded successfully")

    elif os.path.isdir(local_path):
        create_drive_path(drive_path)
        path_id = get_files(drive_path)[0]['id']

        for item in os.listdir(local_path):
            item_path = f"{local_path}/{item}"
            if os.path.isfile(item_path):
                # Avoid check drive directories, because all these elements have the same
                # parent folder, and it is already created (lightweight calls).
                upload_files(item_path, f"{drive_path}/{item}", False)
            elif os.path.isdir(item_path):
                upload_files(item_path, f"{drive_path}/{item}")
    else:
        print("Path is not detected as file or directory. Exiting...")

# ----------------------------------------------------------------------------------------------------------------------


def download_files(drive_path, local_path):
    if not path_exist(drive_path):
        print(f"{drive_path} do not exists in drive. Exiting...")
        return

    if os.path.exists(local_path):
        verbose(f"{local_path} already exists. Exiting...")
        return

    drive_file = get_files(drive_path)[0]
    file_id = drive_file['id']

    if is_drive_dir(drive_file):
        create_local_path(local_path)
        files = list_files(drive_path)

        for file in files:
            if is_drive_dir(file):
                download_files(f"{drive_path}/{file['title']}", f"{local_path}/{file['title']}")
            else:
                download_files(f"{drive_path}/{file['title']}", f"{local_path}/{file['title']}")
    else:
        file_base_name = os.path.basename(drive_path)

        print(f"Downloading {drive_path} file to {local_path}")
        file = drive.CreateFile({'id' : file_id})
        file.GetContentFile(file_base_name)

        shutil.move(file_base_name, local_path)

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    google_auth = authenticate(CREDENTIALS_FILE)
    drive = GoogleDrive(google_auth)

    from time import time
    t0 = time()
    upload_files('aa', '/a/b/c/aa')
    t1 = time()

    print(f"Time elapsed = {t1-t0}")
