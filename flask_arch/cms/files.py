import os
import re
import uuid
import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join

from ..utils import ensure_type
from ..exceptions import INVALID_FNAME, INVALID_FSIZE

SIZE_KB = 1024
SIZE_MB = 1048576

DEFAULT_UPLOAD_DIR='uploads'
DEFAULT_MAX_SIZE=10*SIZE_MB

def get_flen(fp):
    fp.seek(0, 2) # seek to end
    flen = fp.tell() # get size
    fp.seek(0, 0) # seek to beginning
    return flen

def enable_storage(
    upload_dir=DEFAULT_UPLOAD_DIR,
    max_size=DEFAULT_MAX_SIZE,
    regex_whitelist=['jpe?g$', 'png$'],
    subdir_key=None,
):
    def decorator(cls):

        ensure_type(max_size, int, 'max_size')
        ensure_type(regex_whitelist, list, 'regex_whitelist')
        ensure_type(upload_dir, str, 'upload_dir')
        ensure_type(subdir_key, str, 'subdir_key', allow_none=True)

        # rootpath is the base name of the class in lowercase
        files_dir = os.path.join(upload_dir, cls.__name__.split('.')[-1].lower())

        def get_store_dir(self):
            if subdir_key is not None and hasattr(self, subdir_key):
                sub_dir = getattr(self, subdir_key)
                if isinstance(sub_dir, str):
                    store_dir = safe_join(files_dir, sub_dir)
                    if not os.path.exists(store_dir):
                        os.makedirs(store_dir, 0o755)

                    return store_dir
            else:
                return files_dir

        cls.get_store_dir = get_store_dir

        def get_file_path(self, filename):
            store_dir = self.get_store_dir()
            filename = secure_filename(filename)
            path = os.path.join(store_dir, filename)
            print(path)
            if not os.path.isfile(path):
                raise INVALID_FNAME
            return path

        cls.get_file_path = get_file_path

        def stat_file(self, filename):
            path = self.get_file_path(filename)
            return os.stat(path)

        cls.stat_file = stat_file

        def read_file(self, filename, mode='rb'):
            path = self.get_file_path(filename)
            fp = open(path, mode)
            return fp

        cls.read_file = read_file

        def store_file(self, file, store_name=None):
            if len(file.filename) < 1 and file.content_length < 1:
                # annoying flask/werkzeug issue that multiple input form somehow has an empty file
                # do nothing, this is an empty file
                #print("DEBUG: empty file, skipping")  # silently do not save empty files
                return None

            if not os.path.exists(files_dir):
                os.makedirs(files_dir, 0o755)

            # ensure file size within limitation
            flen = get_flen(file)
            if flen > max_size:
                raise INVALID_FSIZE

            # create store_name is left as None
            if not isinstance(store_name, str):
                ext = ''
                if isinstance(file.filename, str):
                    ext_test = file.filename.split('.')[-1]
                    if len(ext_test) > 0:
                        ext = ext_test

                ts_now = int(datetime.datetime.now().timestamp())
                store_name = f'{uuid.uuid4()}-{ts_now}.{ext}'

            # ensure store_name is secured
            store_name = secure_filename(store_name)

            name_allowed = False
            for r in regex_whitelist:
                mt = re.search(r, store_name)
                if mt:
                    name_allowed = True
                    break

            # abort if name not allowed (not matched in whitelist)
            if not name_allowed:
                raise INVALID_FNAME

            store_dir = self.get_store_dir()
            path = os.path.join(store_dir, store_name)

            # save the file
            file.save(path)
            return store_name

        cls.store_file = store_file

        def list_subdir(self):
            if subdir_key is not None and hasattr(self, subdir_key):
                store_dir = self.get_store_dir()
                return os.listdir(store_dir)
            else:
                # no subdir key, do not allow listing, object must save the file's own path
                return []

        cls.list_subdir = list_subdir

        def remove_file(self, filename):
            path = self.get_file_path(filename)
            os.remove(path)

        cls.remove_file = remove_file

        def remove_subdir(self):
            for f in self.list_subdir():
                self.remove_file(f)
            store_dir = self.get_store_dir()
            os.rmdir(store_dir)

        cls.remove_subdir = remove_subdir

        return cls

    return decorator
