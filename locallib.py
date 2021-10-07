import os
import json
import random
import hashlib
from datetime import datetime
from tr4d3r.utils.misc import utcnow


def datetime_stamp():
    return utcnow().strftime('%Y%m%d%H%M%S')

def snapshot_path(root_path):
    folder, file_root = os.path.split(root_path)
    stamp = datetime_stamp()
    file_path = f'{file_root}.{stamp}'
    snap_folder = os.path.join(folder, 'snapshots')
    if not os.path.isdir(snap_folder):
        os.mkdir(snap_folder)
    return os.path.join(snap_folder, file_path)

def blake2b_hash(file_path):
    with open(file_path, 'rb') as f:
        file_hash = hashlib.blake2b()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)

    return file_hash.hexdigest()
