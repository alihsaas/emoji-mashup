from os import listdir
from os.path import isfile, join
from typing import List


def get_files_in_category(path: str) -> List[str]:
    return [
        f for f in listdir(path)
        if isfile(join(path, f))
    ]
