import sys
from typing import List
from abc import ABC, abstractmethod

import pandas as pd

from main import database_manager
from utilities import convert_to_fahrenheit


class Command(ABC):
    """ Interface for command design pattern """

    @abstractmethod
    def execute(self) -> None:
        pass

class CreateMeasurementsTableCommand(Command):
    """ Create measurement database command """

    def __init__(self, table_name:str) -> None:
        self._table_name = table_name

    def execute(self) -> None:
        columns = {"id": "serial PRIMARY KEY",
                    "city": "varchar(20) NOT NULL",
                    "weather_station": "varchar(40) NOT NULL",
                    "celsius": "decimal NOT NULL",
                    "measured_at_ts": "timestamp NOT NULL"}
        database_manager.create_table_if_not_exist(self._table_name, columns)

class AddMeasurementsCommand(Command):
    """ Add measurement to database command """

    def __init__(self, values:dict, table_name:str = "measurement") -> None:
        self._table_name = table_name
        self._values = values

    def execute(self) -> None:
        database_manager.insert(self._table_name, self._values)

class ListMeasurementsCommand(Command):
    """ List Measurements from database Command """

    def __init__(self, filters:tuple = None, columns:List[str] = None, table_name:str = "measurement") -> None:
        self._columns = columns
        self._filters = filters
        self._table_name = table_name

    def execute(self) -> pd.DataFrame:
        results = database_manager.read(self._table_name, self._filters)
        return pd.DataFrame(results, columns=self._columns)

class QuitCommand(Command):
    """ Quit Command """

    def execute(self) -> None:
        sys.exit()

class DisplayResultsCommand(Command):
    """ Display Results Command """

    def __init__(self, measurements_df:pd.DataFrame, country_details_df:pd.DataFrame, target_columns:List[str]) -> None:
        self._measurements_df = measurements_df
        self._country_details_df = country_details_df
        self._target_columns = target_columns

    def execute(self) -> None:
        if self._measurements_df.empty:
            print("No data is available for specified criterias")
        else:
            self._measurements_df = self._measurements_df.merge(self._country_details_df, how="left", on="city")
            self._measurements_df["fahrenheit"] = self._measurements_df["celsius"].apply(lambda cell: convert_to_fahrenheit(cell))
            self._measurements_df["measured_at"] = pd.to_datetime(self._measurements_df["measured_at_ts"]).dt.date
            self._measurements_df = self._measurements_df[self._target_columns]
            print(self._measurements_df)