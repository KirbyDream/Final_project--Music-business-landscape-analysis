import pylab as p
import numpy as np
import pandas as pd

# loading first csv with global record relase data by country, year, genre and format

df = pd.read_csv('./Data/release_data.csv')
# dropping null vallues from "year/country" column
df.dropna(subset=["year"], inplace=True)
df.dropna(subset=["country"], inplace=True)
# checking value count in year column
df_year = df[(df["year"] < 1910)]
df_year.head()
# dropping the rows that have values non related to music format

types = ['All Media', 'File',
         'Floppy Disk', 'DVD', 'Hybrid', 'VHS', 'DVDr',
         '8-Track Cartridge', 'Reel-To-Reel',
         'Memory Stick', 'Betamax', 'HD DVD', 'Cylinder',
         '4-Track Cartridge', 'VHD', 'Blu-ray-R', 'U-matic',
         'Film Reel', 'SelectaVision', 'MiniDV', 'Video8', 'Betacam SP',
         'PlayTape', 'Video 2000', 'Wire Recording', 'Betacam', 'Tefifon',
         'Pocket Rocker', 'Cartrivision', 'HD DVD-R', 'RCA Tape Cartridge', 'UMD', 'Box Set', 'CDV', 'Flexi-disc']

new_df = df[df["format"].str.contains('|'.join(types)) == False]

# grouping similar formats into one common format

new_df = new_df.replace(to_replace=['Lathe Cut', 'Acetate', 'Edison Disc', 'Pathé Disc', 'Shellac'],
                        value="Vinyl")
new_df = new_df.replace(to_replace=['Minidisc', 'MVD', 'Laserdisc', 'DCC', 'SACD', 'Blu-ray', 'DualDisc'],
                        value="CD")
new_df = new_df.replace(to_replace=['DC-International', 'NT Cassette', 'Elcaset', 'Microcassette', 'DAT', 'Blu-ray', 'DualDisc'],
                        value='Cassette')
# checking the min value in year, and dropping all the values in years before 1950
new_df['year'].min()
new_df = new_df[(new_df["year"] > 1950)]

# dropping year 2020, because of missing data
new_df = new_df[(new_df["year"] < 2020)]

global_release = new_df
# checking data types
global_release.dtypes
# converting year value into int
global_release['year'] = global_release['year'].astype(int)
my_df = global_release
# grouping by country, year and format. format as count
# to have aggregated data
df_year_country_genre = my_df.groupby(["year", "country", "format", "genre"])[
    "format"].count().reset_index(name="records_count")
df_year_country_genre.sample()
# exporting to CSV

df_year_country_genre.to_csv("./Data/csv/format_release.csv", index=False)
