import logging
from typing import List
from pathlib import Path
from datetime import datetime, timedelta
from collections import namedtuple

from database_manager import DatabaseManager
from documents import JSONDocument, XMLDocument
from weather_station import WeatherStation
from utilities import get_sub_paths
from commands import *

import pandas as pd

pd.options.display.max_rows = 1000

db_credentials = JSONDocument(path=Path().cwd().joinpath("config", "database_credentials.json")).get_data()
database_manager = DatabaseManager(user=db_credentials["user"],
                                password=db_credentials["password"],
                                service_name=db_credentials["service_name"],
                                port=db_credentials["port"],
                                database_name=db_credentials["database_name"],
                                dialect=db_credentials["dialect"])

logging.basicConfig(filename="system.log",
                    format="%(asctime)s - [module: %(module)s, method: %(funcName)s, line: %(lineno)d] - %(levelname)s -  %(message)s",
                    datefmt="%d.%m.%Y %H:%M:%S")

def write_measurements_data_to_database(input_path:Path, suffix:str = "xml") -> None:
    """ Writete measurements data to database """
    measurements_raw_data_paths = get_sub_paths(input_path, pattern=f"*.{suffix}")
    weather_stations = get_weather_stations(measurements_raw_data_paths)
    for weather_station in weather_stations:
        cleaned_measurements = weather_station.prepare_measurements()
        add_measurements_command = AddMeasurementsCommand(values=cleaned_measurements)
        add_measurements_command.execute()

def list_measurements(target_datetime:datetime, city_name:str) -> pd.DataFrame:
    """ List measurements from database """
    FilterCriteria = namedtuple("FilterCriteria", ["column_name", "value", "operator"])
    columns = ["id", "city", "weather_station", "celsius", "measured_at_ts"]
    filter_criterias = (FilterCriteria(column_name="measured_at_ts", value=target_datetime, operator=">="),
                          FilterCriteria(column_name="city", value=city_name, operator="="))

    list_measurements_command = ListMeasurementsCommand(columns=columns, filters=filter_criterias)
    measurements_df = list_measurements_command.execute()

    return measurements_df

def get_weather_stations(soruce_paths:dict) -> List[WeatherStation]:
    """ Get weather stations """
    weather_stations = []
    for station_name, station_raw_data_paths in soruce_paths.items():
        measurements = get_measurements(station_raw_data_paths)
        new_weather_station = WeatherStation(name=station_name, measurements=measurements)
        weather_stations.append(new_weather_station)

    return weather_stations

def get_measurements(raw_data_paths:List[Path]) -> List[dict]:
    """ Get measurements data from document(s) """
    measurements = []
    for raw_data_path in raw_data_paths:
        try:
            new_measurement = XMLDocument(path=raw_data_path).get_data()
            measurements.append(new_measurement)
        except Exception as e:
            logging.warning(f"Failed to read file from path {raw_data_path}: {str(e)}")
            continue

    return measurements

def get_country_mapping_as_df(source_path:Path, suffix="json") -> pd.DataFrame:
    """ Get country mapping from input files """
    country_file_paths = get_sub_paths(source_path, pattern=f"*.{suffix}")
    country_content = []
    for country_file_path in country_file_paths.values():
        new_content = JSONDocument(path=country_file_path).get_data()
        new_content["city"] = new_content["city"].title()
        new_content["country"] =  new_content["country"].title()
        country_content.append(new_content)

    return pd.DataFrame(country_content)

if __name__ == "__main__":
    create_measurements_table_command = CreateMeasurementsTableCommand(table_name="measurement")
    create_measurements_table_command.execute()

    countries_source_path = Path().cwd().joinpath("config", "countries")
    country_details_df = get_country_mapping_as_df(countries_source_path)

    measurements_source_path = Path().cwd().joinpath("data")
    write_measurements_data_to_database(measurements_source_path)

    target_columns = ["city", "country", "population_M", "celsius", "fahrenheit", "measured_at"]
    target_day = 20
    while True:
        try:
            user_input = input("Please type city name to see the last 3 days temprature values(Type q\Q to quit): ").title()
            if user_input == "Q":
                QuitCommand().execute()

            city_name = user_input
        except Exception as e:
            print("Please try again.")
            continue
        else:
            target_datetime = datetime.now() - timedelta(days=target_day)
            measurements_df = list_measurements(target_datetime, city_name)

            display_results_command = DisplayResultsCommand(measurements_df=measurements_df,
                                                        country_details_df=country_details_df,
                                                        target_columns=target_columns)
            display_results_command.execute()





