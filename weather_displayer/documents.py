import json
from typing import Union
from abc import ABC, abstractmethod
from pathlib import Path
from functools import wraps

import pandas as pd
import xml.etree.ElementTree as et

from errors import FileError


def catch_error(operation:object) -> object:
    """ Error catching decorator """
    @wraps(operation)
    def wrapped(self, *args, **kwargs):
        try:
            return operation(self, *args, **kwargs)
        except Exception as e:
            raise FileError(str(e))

    return wrapped

class Document(ABC):
    """ Interface for different document types """

    def __init__(self,  path:Union[Path, str]) -> None:
        self._path = path

    @abstractmethod
    def get_data(self):
        pass

    def __repr__(self) -> str:
        return f"{self._path}"

class XMLDocument(Document):
    """ XML Document """

    def __init__(self, path:Union[Path, str]) -> None:
        super().__init__(path)

    #TODO: Think recursively
    @catch_error
    def get_data(self) -> dict:
        measurements = {}
        xml_tree = et.parse(self._path)
        root_node = xml_tree.getroot()
        for element in root_node:
            if not element.text.strip():
                for sub_element in element:
                    unit = list(sub_element.attrib.values())[0]
                    measurements[unit] = float(sub_element.text.strip())
            else:
                measurements[element.tag] = element.text

        return  measurements

class JSONDocument(Document):
    """ JSON Document """

    def __init__(self, path:Union[Path, str]) -> None:
        super().__init__(path)

    @catch_error
    def get_data(self) -> dict:
        with open(self._path, 'r') as f:
            content = json.load(f)
        return content

    def __repr__(self) -> str:
        return f"{self._path}"