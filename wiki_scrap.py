import os

import json
import requests
import pyjsonviewer
from functools import reduce
import operator

import pandas as pd
import numpy as np

import requests
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
from numpy import int64

from dotenv import load_dotenv
load_dotenv()

# scrapping wikipedia page for data about vinyl sales
url = "https://en.wikipedia.org/wiki/Vinyl_revival"
s = requests.Session()
response = s.get(url)
print(response.status_code)

soup = BeautifulSoup(response.content, "html.parser")
tags = soup.find("table", {"class": "wikitable"})
my_table = pd.read_html(tags.prettify())
table = my_table[0]
table.sample()
clean_table = table


def cleaning_df_data(raw_dataframe):
    """Dropping irrelevent data and removing special characters to have a dataset of clean numbers"""
    # remove brackets and parenthesis from values
    raw_dataframe = raw_dataframe.replace('[\(\[].*?[\)\]]', '', regex=True)
    raw_dataframe = raw_dataframe.drop(index=0)
    raw_dataframe = raw_dataframe.drop(index=11)
    raw_dataframe = raw_dataframe.replace(',', '', regex=True)
    raw_dataframe = raw_dataframe.replace('–', '', regex=True)
    raw_dataframe = raw_dataframe.replace('', 0)
    raw_dataframe = raw_dataframe.replace('\+', '', regex=True)
    raw_dataframe = raw_dataframe.replace('±', '', regex=True)
    raw_dataframe = raw_dataframe.replace('-', 0)
    return raw_dataframe


clean_df = cleaning_df_data(clean_table)

# pivoting the table using the melt function in order to have Countries,years and value as columns
clean_melt = clean_df.melt(
    id_vars=['Countries'], var_name='Year', value_name='value').sort_values('Year')
clean_melt.reset_index(inplace=True)

# changing values expressed in m "million" to explicit values

clean_melt.at[211, 'value'] = '3200000'
clean_melt.at[231, 'value'] = '4200000'
clean_melt.at[259, 'value'] = '0'
clean_melt = clean_melt.dropna()

clean_melt.isnull().sum()

# some countries have the record sales split between LP/SP
# we iterate over the countries with split values and sum them into a single row
for index, row in clean_melt.iterrows():
    for index2, row2 in clean_melt.iterrows():
        if row["Year"] == row2["Year"] + ".1":
            if row["value"] != row2["value"] and row["Countries"] == row2["Countries"]:
                clean_melt.loc[index, "value"] = int64(
                    row2["value"]) + int64(row["value"])
                # print(index)
                # print(clean_melt.loc[index,"Countries"])
                # print(clean_melt.loc[index,"value"])

clean_melt = clean_melt[clean_melt["Year"].str.contains("\.1") == True]
clean_melt = clean_melt.replace('\.1', "", regex=True)
clean_melt.reset_index(inplace=True)
clean_melt.drop(['level_0', 'index'], axis=1, inplace=True)

# dropping column for missing values
clean_melt = clean_melt[clean_melt["Year"].str.contains("2019") == False]

# converting date type
clean_melt["Year"] = pd.to_datetime(clean_melt["Year"])

# converting value type
clean_melt = clean_melt.astype({'value': 'int32'})
clean_melt.dtypes

clean_melt.to_csv("./Data/csv/wiki_scrap.csv", index=False)
