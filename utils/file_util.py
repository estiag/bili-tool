import zipfile


def is_zipfile(file_path):
    try:
        with open(file_path, 'rb') as file:
            return zipfile.is_zipfile(file)
    except FileNotFoundError:
        return False
