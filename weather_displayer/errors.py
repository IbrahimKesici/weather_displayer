
class BaseError(Exception):
    """ Base convertion error """

class FileError(BaseError):
    """ Raised when an error occurs on file operation(s)"""

class DatabaseError(BaseError):
    """ Raised when a database related operation fails """