from typing import List
from dataclasses import dataclass

import pandas as pd

from utilities import convert_to_celcius



@dataclass(repr=True)
class WeatherStation():
    name:str
    measurements: List[dict]

    def prepare_measurements(self, convert_to_dict:bool = True) -> pd.DataFrame:
        """ Prepare data for the operations: cleaning, manipulating etc. """
        measurements_df = pd.DataFrame(self.measurements)
        measurements_df["weather_station"] = self.name
        measurements_df["city"] = measurements_df["city"].str.title()
        measurements_df["measured_at_ts"] = measurements_df["measured_at_ts"].astype("datetime64[ns]")

        measurements_df["celsius"] = measurements_df.apply(lambda row: self._convert_to_celcius(row), axis=1)
        measurements_df.drop("fahrenheit", axis=1, inplace=True, errors="ignore")

        return measurements_df.to_dict("records") if convert_to_dict else measurements_df

    def _convert_to_celcius(self, row:pd.Series) -> float:
        celcius_value = row.get("celsius")
        fahrenheit_value = row.get("fahrenheit")
        if pd.isnull(celcius_value) and pd.notnull(fahrenheit_value):
            return convert_to_celcius(fahrenheit_value)
        else:
            return celcius_value