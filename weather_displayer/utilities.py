from typing import Union
from pathlib import Path


def convert_to_fahrenheit(value:float) -> float:
    """ Convert celsius temprature to fahrenheit """
    return round((float(value) * 1.8) + 32, 2)

def convert_to_celcius(value:float) -> float:
    """ Convert fahrenheit to celsiuse """
    return round((float(value) - 32) / 1.8, 2)

def get_sub_paths(root_path:Union[str, Path], pattern:str = "**/") -> dict:
    """ Get all subpaths from the root path(s) """
    sub_paths ={}
    for child_path in root_path.iterdir():
        folder_name = child_path.name
        file_paths = list(child_path.rglob(pattern))
        sub_paths[folder_name] = file_paths or child_path

    return sub_paths