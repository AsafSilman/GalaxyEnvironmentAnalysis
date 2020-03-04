from pathlib import Path

from src.utils.move_files_in_list import move_files_in_list
from src.utils.rm_tree import rm_tree

def move_data(config, directory):
    data_interim_path = Path(config.get('data_interim_path', 'data/interim'))

    image_files = list(data_interim_path.glob("**/*.png"))

    move_files_in_list(image_files, directory,)

    rm_tree(data_interim_path)