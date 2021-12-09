import logging
from typing import List

from sqlalchemy import create_engine, inspect
from errors import DatabaseError


class Singleton():
    """ Singleton Class"""
    _instance = None

    def __new__(cls, *args, **kwargs) -> object:
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

class DatabaseManager(Singleton):
    """ Database Manager for CR operations """

    def __init__(self, user:str, password:str, service_name:str, port:int, database_name:str, dialect:str) -> None:
        connection_str = f"{dialect}://{user}:{password}@{service_name}:{port}/{database_name}"
        self._engine = create_engine(connection_str)

    def create_table_if_not_exist(self, table_name:str, columns:dict) -> None:
        """ Create table if not exist on database """
        if not inspect(self._engine).has_table(table_name):
            columns_with_types = [f"{column_name} {data_type}" for column_name, data_type in columns.items()]
            statement = f"""CREATE TABLE {table_name}
                            ({", ".join(columns_with_types)});
                        """
            self._execute(statement)

    def read(self, table_name:str, criterias:tuple=None) -> None:
        """ Fetch data from database based on criteria(s) """
        statement = f"SELECT * FROM {table_name}"
        values = None
        if criterias:
            placeholders = [f"{criteria.column_name} {criteria.operator} %s" for criteria in criterias]
            select_criteria = ' AND '.join(placeholders)
            values = [criteria.value for criteria in criterias]

            statement += f" WHERE {select_criteria}"

        return self._execute(statement, values).fetchall()

    def insert(self, table_name:str, data:List[dict]) -> None:
        """ Insert one/multiple records to database """
        columns = data[0].keys()
        column_names = ", ".join(columns)
        placeholders = ", ".join([f"%({column})s" for column in columns])
        statement = f"""INSERT INTO {table_name} ({column_names})
                        VALUES ({placeholders})"""

        self._execute(statement, data)

    def _execute(self, statement:str, data:List[tuple] = None):
        """ Execute sql statement(s) with placeholders """
        try:
            with self._engine.connect() as connection:
                return connection.execute(statement, data or [])
        except Exception as e:
            logging.error(f"Database operation is failed {str(e)}")
            raise DatabaseError(f"Database operation is failed {str(e)}")