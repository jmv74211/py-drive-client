from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth


# ----------------------------------------------------------------------------------------------------------------------

CREDENTIALS_FILE = 'credentials.json'

# ----------------------------------------------------------------------------------------------------------------------


def authenticate(credentials_file):
    google_auth = GoogleAuth()
    google_auth.LoadCredentialsFile(credentials_file)

    if google_auth.credentials is None:
        google_auth.LocalWebserverAuth()
    elif google_auth.access_token_expired:
        google_auth.Refresh()
    else:
        google_auth.Authorize()

    google_auth.SaveCredentialsFile(credentials_file)

    return google_auth

# ----------------------------------------------------------------------------------------------------------------------


def is_dir(file_data):
    return file_data['mimeType'] == 'application/vnd.google-apps.folder'

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
    if is_dir(files[0]):
        files = drive.ListFile({'q': f"'{files[0]['id']}' in parents"}).GetList()

    return files

# ----------------------------------------------------------------------------------------------------------------------


def path_exist(path):
    return len(get_files(path)) > 0

# ----------------------------------------------------------------------------------------------------------------------


def create_path(path):
    if not path_exist(path):

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
            files = get_files(path_built)

    print(f"Created path --> {path}")

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    google_auth = authenticate(CREDENTIALS_FILE)
    drive = GoogleDrive(google_auth)

    # files = list_files('/')
    # files = get_files('/apps/test')

    # for file in files:
    #     print(f"title = {file['title']} -- id = {file['id']}")
    # # print(path_exist('/pepe'))

    # files = list_files('/apps/test/do_not_delete.txt')

    # for file in files:
    #     print(f"title = {file['title']} -- id = {file['id']}")

    # print("UPLOADING")
    # file5 = drive.CreateFile({'parents': [{'id': }]})
    # file5.SetContentFile('test.jpg')
    # file5.Upload()
    # print("UPLOADED")

    create_path('/aaa/bbb')

    # folder = drive.CreateFile({'parents': [{'id': 'root'}], 'title': 'pepe',
    #                            'mimeType': 'application/vnd.google-apps.folder'})
    # folder.Upload()
